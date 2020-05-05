from .pagination import CursorPaginator
from ..resolvers.mixins import ListModelMixin


class RelayModelMixin(ListModelMixin):
    pagination_class = CursorPaginator

    def get_ordering(self):
        if hasattr(self, "ordering"):
            return self.ordering
        return ("id",)

    def paginate_queryset(self, queryset, **kwargs):
        kwargs.update(
            dict(
                ordering=self.get_ordering(),
                first=self.operation_kwargs.get("first", None),
                last=self.operation_kwargs.get("last", None),
                after=self.operation_kwargs.get("after", None),
                before=self.operation_kwargs.get("before", None),
            )
        )
        return super().paginate_queryset(queryset, **kwargs)

    def list(self, request, *args, **kwargs):
        page = super().list(request, *args, **kwargs)
        return {
            "edges": [{"cursor": page.cursor(node), "node": node} for node in page],
            "pageInfo": page,
        }
