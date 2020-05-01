from unittest.mock import patch, Mock

from ariadne_extended.resolvers import ListModelResolver, ModelResolver, Resolver


class ChildResolver(Resolver):
    def stub_resolve_method(self, *args, **kwargs):
        pass


@patch("ariadne_extended.resolvers.ListModelResolver.initial")
@patch("ariadne_extended.resolvers.ListModelResolver.list")
def test_resolve_uses_proper_method(mock_list, mock_initial):
    mock_list.return_value = "handler called"
    resolver = ListModelResolver(None, None)
    resolver.config = {"method": "list"}

    fn = resolver.resolve(None)
    mock_initial.assert_called()

    assert fn == "handler called"


@patch("ariadne_extended.resolvers.ModelResolver.initial")
@patch("ariadne_extended.resolvers.ModelResolver.retrieve")
def test_resolve_uses_retrieve_by_default(mock_retrieve, mock_initial):
    mock_retrieve.return_value = "handler called"
    resolver = ModelResolver(None, None)
    resolver.config = {}

    fn = resolver.resolve(None)
    mock_initial.assert_called()

    assert fn == "handler called"

