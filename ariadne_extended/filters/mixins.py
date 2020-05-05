from .backends import GraphQLFilterBackend


class FilterMixin:
    filter_backends = [GraphQLFilterBackend]
    filter_arg = "filter"

    def get_filter_backends(self):
        return self.filter_backends

    def get_filter_arg(self):
        return self.filter_arg

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.info, queryset, self)
        return queryset

    def get_filter_data(self):
        """
        Called by the filter backend when determining how to filter
        """
        if self.config.get("reference", False):
            return self.reference_kwargs
        return self.operation_kwargs.get(self.filter_arg, {})

    def get_queryset(self):
        qs = super().get_queryset()
        return self.filter_queryset(qs)
