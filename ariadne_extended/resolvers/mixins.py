"""
Mixins that are in DRF serializers and resolver data
"""
import enum

from django.db.models.deletion import IntegrityError, ProtectedError


class ListModelMixin:
    """
    List a queryset.
    """

    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            return page

        return queryset

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset, **kwargs):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self, **kwargs)


class InputMixin:
    """
    Take an input operation argument and return the data.

    This mixin is pretty limited, nested enums under other input types will not be
    converted into their value. FIX/CHANGE
    """

    input_arg = "input"
    convert_enums = True

    def get_input_arg(self):
        return self.input_arg

    def get_input_data(self):
        input_data = self.operation_kwargs.get(self.input_arg, {}).copy()
        # Get and convert any translated enums into their values
        # May be able to be moved to a serializer save point for models?
        # As having access to the enum may be useful in other contexts
        if self.convert_enums:
            if isinstance(input_data, dict):
                self.process_dict(input_data)

            if isinstance(input_data, list):
                for data in input_data:
                    if isinstance(data, dict):
                        data = self.process_dict(data)

        return input_data

    def process_dict(self, input_data):
        for key, value in input_data.items():
            if isinstance(value, enum.Enum):
                # Get and set actual value of enum
                input_data[key] = value.value


class CreateModelMixin(InputMixin):
    def create(self, parent, *args, **kwargs):
        serializer = self.get_serializer(data=self.get_input_data())
        valid = serializer.is_valid(raise_exception=False)
        if valid:
            obj = self.perform_create(serializer)
        else:
            obj = serializer.data
        return dict(success=valid, object=obj, errors=serializer.errors)

    def perform_create(self, serializer):
        return serializer.save()


class UpdateModelMixin:
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=self.get_input_data(), partial=partial)
        valid = serializer.is_valid(raise_exception=False)

        obj = instance
        if valid:
            obj = self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return dict(success=valid, object=obj, errors=serializer.errors)

    def perform_update(self, serializer):
        return serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class DestroyModelMixin:
    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id = instance.id
        count = False
        errors = {}
        try:
            count, _ = self.perform_destroy(instance)
        except (IntegrityError, ProtectedError) as e:
            errors = {"destroy": [str(e)]}
        return {"success": bool(count), "errors": errors, "object": {"id": instance_id}}

    def perform_destroy(self, instance):
        return instance.delete()
