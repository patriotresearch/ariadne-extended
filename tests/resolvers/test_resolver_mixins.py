from ariadne_extended.resolvers.model import GenericModelResolver
from enum import Enum
from unittest.mock import patch

from ariadne_extended.resolvers import ListModelResolver, ModelResolver, Resolver
from ariadne_extended.resolvers.mixins import InputMixin, RetrieveModelMixin


class ChildResolver(Resolver):
    def stub_resolve_method(self, *args, **kwargs):
        pass


def test_input_mixin_attrs():
    assert InputMixin.input_arg == "input"
    assert InputMixin.convert_enums is True


def test_input_mixin_get_input_arg():
    class AlteredInputMixin(InputMixin):
        input_arg = "another_input"

    arg = InputMixin().get_input_arg()
    assert arg == "input"

    arg = AlteredInputMixin().get_input_arg()
    assert arg == "another_input"


@patch("ariadne_extended.resolvers.ListModelResolver.initial")
@patch("ariadne_extended.resolvers.ListModelResolver.list")
def test_resolve_uses_proper_method(mock_list, mock_initial):
    mock_list.return_value = "handler called"
    resolver = ListModelResolver("parent", "info")
    resolver.config = {"method": "list"}

    fn = resolver.resolve("resolve_parent")
    mock_initial.assert_called_once_with()

    assert fn == "handler called"


@patch("ariadne_extended.resolvers.ModelResolver.initial")
@patch("ariadne_extended.resolvers.ModelResolver.retrieve")
def test_resolve_uses_retrieve_by_default(mock_retrieve, mock_initial):
    mock_retrieve.return_value = "handler called"
    resolver = ModelResolver("parent", "info")
    resolver.config = {}

    fn = resolver.resolve("resolve_parent")
    mock_initial.assert_called_once_with()

    assert fn == "handler called"


class Hello(Enum):
    HELLO = "hello"


class TestInputMixin:
    def test_get_input_data_with_enum_in_dict(self):
        im = InputMixin()
        im.operation_kwargs = {"input": {"hello": "world", "enum": Hello.HELLO}}

        result = im.get_input_data()

        assert result == {"hello": "world", "enum": "hello"}

    def test_get_input_data_with_enum_in_list(self):
        im = InputMixin()
        im.operation_kwargs = {"input": [{"hello": "world", "enum": Hello.HELLO}]}

        result = im.get_input_data()

        assert result == [{"hello": "world", "enum": "hello"}]

    def test_get_input_data_with_no_enum_in_list(self):
        im = InputMixin()
        im.operation_kwargs = {"input": [1, 2, 3]}

        result = im.get_input_data()

        assert result == [1, 2, 3]


@patch("ariadne_extended.resolvers.model.GenericModelResolver.get_object")
def test_retrieve_model_mixin(mock_get_object):
    mock_get_object.return_value = "A model"

    class Mixin(RetrieveModelMixin, GenericModelResolver):
        queryset = "Unused"

    detail_resolver = Mixin("parent", "info", id=123)
    returned = detail_resolver.retrieve(None)

    # Nothing passed into get_object
    mock_get_object.assert_called_once_with()
    # retrieve just returns what get_object returns
    assert returned == "A model"
