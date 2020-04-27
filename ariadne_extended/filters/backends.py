from django_filters.rest_framework import DjangoFilterBackend


class GraphQLFilterBackend(DjangoFilterBackend):
    """Provide filter data from the resolver to the filterset"""

    def get_filterset_kwargs(self, request, queryset, resolver):
        return {"data": resolver.get_filter_data(), "queryset": queryset, "request": request}
