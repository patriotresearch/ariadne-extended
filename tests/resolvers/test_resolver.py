from unittest.mock import patch

from ariadne import QueryType, make_executable_schema
from ariadne_extended.resolvers import Resolver
from glom import glom
from graphql import graphql_sync, GraphQLResolveInfo


def fake_info(**kwargs):
    bits = dict(
        field_name="name",
        field_nodes=[],
        return_type="GraphQLOutputType",
        parent_type="GraphQLObjectType",
        path="",
        schema="GraphQLSchema",
        fragments=dict(),
        root_value=dict(),
        operation=None,
        variable_values=None,
        context=None,
        # is_awaitable=lambda x: x,
    )
    bits.update(kwargs)
    return GraphQLResolveInfo(**bits)


def test_resolver_e2e():
    class ThisResolver(Resolver):
        def retrieve(self, *args, some_arg=None, **kwargs):
            return dict(id=123, name="Something named", additional=some_arg, comes=True)

    type_defs = """
        type SomethingType {
            id: ID!
            name: String
            additional: String
            comes: Boolean
        }

        type Query {
            getThing(someArg: String): SomethingType
        }
    """

    query = QueryType()

    query.set_field("getThing", ThisResolver.as_resolver())

    resolvers = [query]
    schema = make_executable_schema(type_defs, resolvers)

    result = graphql_sync(
        schema,
        """
            query {
                thing: getThing(someArg: "This Way") {
                    id
                    name
                    additional
                    comes
                }
            }
        """,
    )
    assert result.errors is None
    assert glom(result.data, "thing.id") == "123"
    assert glom(result.data, "thing.name") == "Something named"
    assert glom(result.data, "thing.additional") == "This Way"
    assert glom(result.data, "thing.comes") is True


class ChildResolver(Resolver):
    default_method = "new_default_method"

    def new_default_method(self, *args, **kwargs):
        pass

    def stub_resolve_method(self, *args, **kwargs):
        pass


def test_attrs():
    assert Resolver.permission_classes == []
    assert Resolver.throttle_classes == []
    assert Resolver.authentication_classes == []
    assert Resolver.default_method == "retrieve"


@patch("ariadne_extended.resolvers.Resolver.get_operation_args")
@patch("ariadne_extended.resolvers.Resolver.get_operation_kwargs")
@patch("ariadne_extended.resolvers.Resolver.get_reference_kwargs")
def test_resolver_initial_args(
    mock_get_reference_kwargs, mock_get_operation_kwargs, mock_get_operation_args
):
    mock_get_operation_args.return_value = "translated_args"
    mock_get_operation_kwargs.return_value = "translated_kwargs"
    mock_get_reference_kwargs.return_value = "translated_ref_kwargs"
    parent = "parent_obj"
    info = fake_info(context="request")

    resolver = ChildResolver(
        parent,
        info,
        {"operation": "args"},
        True,
        config=dict(test="config"),
        additional_operation="kwarg",
    )

    mock_get_operation_kwargs.assert_called()

    assert resolver.info == info
    assert resolver.request == "request"
    assert resolver.parent == parent
    assert resolver.config == dict(test="config")
    assert resolver._operation_args == (dict(operation="args"), True)
    assert resolver._operation_kwargs == dict(additional_operation="kwarg")
    assert resolver.operation_kwargs == "translated_kwargs"
    assert resolver.operation_args == "translated_args"
    assert resolver.reference_kwargs == "translated_ref_kwargs"


def test_initial(mocker):
    """
    Initial method gets passed handler args and kwargs and checks different
    """
    mock_perf_auth = mocker.patch("ariadne_extended.resolvers.Resolver.perform_authentication")
    mock_check_permissions = mocker.patch("ariadne_extended.resolvers.Resolver.check_permissions")
    mock_check_throttles = mocker.patch("ariadne_extended.resolvers.Resolver.check_throttles")

    resolver_instance = ChildResolver("parent", fake_info())
    assert resolver_instance.initial("info_obj", "additional_arg", some_kwargs=True) is None

    mock_perf_auth.assert_called_with("info_obj")
    mock_check_permissions.assert_called_with("info_obj")
    mock_check_throttles.assert_called_with("info_obj")


def test_resolve(mocker):
    """
    Uses configuration resolver handler method if present
    """
    mock_initial = mocker.patch("ariadne_extended.resolvers.Resolver.initial")
    method_spy = mocker.spy(ChildResolver, "stub_resolve_method")
    resolver_instance = ChildResolver(
        "parent", fake_info(), config=dict(method="stub_resolve_method")
    )

    resolver_instance.resolve("parent", "additional_arg", some_kwargs=True)
    mock_initial.assert_called_with(fake_info(), "additional_arg", some_kwargs=True)
    method_spy.assert_called_with(resolver_instance, "parent", "additional_arg", some_kwargs=True)


def test_resolve_default(mocker):
    """
    Falls back on default resolver handler method if none specified
    """
    mock_initial = mocker.patch("ariadne_extended.resolvers.Resolver.initial")
    method_spy = mocker.spy(ChildResolver, "new_default_method")
    stub_method_spy = mocker.spy(ChildResolver, "stub_resolve_method")

    resolver_instance = ChildResolver("parent", fake_info())

    resolver_instance.resolve("parent", "additional_arg", some_kwargs=True)
    mock_initial.assert_called_with(fake_info(), "additional_arg", some_kwargs=True)
    method_spy.assert_called_with(resolver_instance, "parent", "additional_arg", some_kwargs=True)
    stub_method_spy.assert_not_called()


# def test_operation_args(mocker):
# def test_operation_kwargs(mocker):
# def test_reference_kwargs(mocker):
# def test_get_serializer(mocker):
# def test_get_serializer_class(mocker):
# def test_get_serializer_context(mocker):

# def test_as_resolver(mocker):
#     method_spy = mocker.spy(ChildResolver, "stub_resolve_method")
#     # resolve_spy = mocker.spy(ChildResolver, "resolve")
#     resolver = ChildResolver.as_resolver(config_kwargs=False, method="stub_resolve_method")
#     # inited_resolver = Mock()
#     # inited_resolver.operation_args = ("waka", )
#     # inited_resolver.operation_kwargs = {"something": "else"}
#     # inited_resolver.retrieve = Mock()
#     # mock_init.return_value = inited_resolver
#     assert resolver.resolver_class == ChildResolver

#     # returns resolver function that takes resolver arguments from ariadne
#     resolver("parent", "info_obj", "additional_arg", some="kwargs")
#     # mock_init.assert_called_with(
#     #     "parent", "info_obj", "additional_arg", some="kwargs", config={"config_kwargs": False},
#     # )
#     # resolve_spy.assert_called_with(instance, "parent", "additional_arg", some="kwargs")
#     method_spy.assert_called_with("parent", "additional_arg", some="kwargs")

# def test_as_resolver(mocker):
#     init = mocker.patch("ariadne_extended.resolvers.Resolver.__init__")
#     init.return_value = None


@patch("ariadne_extended.resolvers.Resolver.as_resolver")
def test_as_nested_resolver(mock_as_resolver):
    """
    Calls `as_resolver` with nested config kwarg
    """
    ChildResolver.as_nested_resolver(additional_kwargs=True)
    mock_as_resolver.assert_called_with(nested=True, additional_kwargs=True)


@patch("ariadne_extended.resolvers.Resolver.as_resolver")
def test_as_reference_resolver(mock_as_resolver):
    """
    Calls `as_resolver` with reference config kwarg
    """
    ChildResolver.as_reference_resolver(additional_kwargs=True)
    mock_as_resolver.assert_called_with(reference=True, additional_kwargs=True)


# def test_all_the_cloned_drf_methods
