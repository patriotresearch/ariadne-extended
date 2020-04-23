from unittest.mock import patch

from ariadne_extended.resolvers import ListModelResolver, ModelResolver, Resolver
from ariadne_extended.utils.abc import concreter

ConcreteResolver = concreter(Resolver)


@patch("graph.resolvers.ListModelResolver.initial")
@patch("graph.resolvers.ListModelResolver.list")
def test_resolve_uses_proper_method(mock_list, mock_initial):
    mock_list.return_value = "handler called"
    resolver = ListModelResolver(None, None)
    resolver.config = {"method": "list"}

    fn = resolver.resolve(None)
    mock_initial.assert_called()

    assert fn == "handler called"


@patch("graph.resolvers.ModelResolver.initial")
@patch("graph.resolvers.ModelResolver.retrieve")
def test_resolve_uses_retrieve_by_default(mock_retrieve, mock_initial):
    mock_retrieve.return_value = "handler called"
    resolver = ModelResolver(None, None)
    resolver.config = {}

    fn = resolver.resolve(None)
    mock_initial.assert_called()

    assert fn == "handler called"


@patch("graph.resolvers.Resolver.get_operation_kwargs")
def test_resolver_initial_args(mock_get_operation_kwargs):
    mock_get_operation_kwargs.return_value = "translated_kwargs"
    parent = "parent_obj"
    info = "info_obj"

    resolver = ConcreteResolver(
        parent, info, config=dict(test="config"), additional_operation="kwarg"
    )

    mock_get_operation_kwargs.assert_called()

    assert resolver.info == info
    assert resolver.request == info
    assert resolver.parent == parent
    assert resolver.config == dict(test="config")
    assert resolver._operation_kwargs == dict(additional_operation="kwarg")
    assert resolver.operation_kwargs == "translated_kwargs"
