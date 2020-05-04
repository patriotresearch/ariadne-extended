from ariadne_extended.resolvers.model import ModelResolver

from .mixins import RelayModelMixin
from ariadne import FallbackResolversSetter
from .types import page_info
from graphql.type import GraphQLField

__resolvers__ = ["page_info_resolver"]


@page_info.field("count")
def resolve_page_info_count(parent, info, *args, **kwargs):
    page = parent.get("cursor", None)
    return page.paginator.queryset.count()


def resolve_page_info(parent, info, *args, **kwargs) -> dict:
    page = parent.get("pageInfo", None)
    try:
        end_cursor = page.cursor(page[-1])
    except IndexError:
        end_cursor = None
    try:
        start_cursor = page.cursor(page[0])
    except IndexError:
        start_cursor = None
    return {
        "hasNextPage": page.has_next,
        "hasPreviousPage": page.has_previous,
        "startCursor": start_cursor,
        "endCursor": end_cursor,
        "has_next_page": page.has_next,
        "has_previous_page": page.has_previous,
        "start_cursor": start_cursor,
        "end_cursor": end_cursor,
        "cursor": page,
    }


class CustomPageInfoResolver(FallbackResolversSetter):
    def add_resolver_to_field(self, name: str, field_object: GraphQLField) -> None:
        if name == "pageInfo" and field_object.resolve is None:
            field_object.resolve = resolve_page_info


page_info_resolver = CustomPageInfoResolver()


class RelayModelResolver(RelayModelMixin, ModelResolver):
    """
    Model resolver that provides cursor based pagination
    """

    pass
