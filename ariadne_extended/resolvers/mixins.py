"""
Mixins that are in DRF serializers and resolver data
"""
import enum

from django.db.models.deletion import IntegrityError, ProtectedError
from . import exceptions


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
            # This will break shit
            obj = None
        return dict(success=valid, object=obj, errors=serializer.errors)

    def perform_create(self, serializer):
        return serializer.save()


class DetailModelMixin:
    lookup_arg = None
    lookup_field = "id"

    def get_lookup_arg(self):
        return self.config.get("lookup_arg", self.lookup_arg)

    def get_lookup_field(self):
        return self.config.get("lookup_field", self.lookup_field)

    def get_lookup_operation_data(self):
        if self.config.get("reference", False):
            return self.reference_kwargs
        return self.operation_kwargs

    def get_lookup_filter_kwargs(self):
        # Perform the lookup filtering.
        lookup_arg = self.get_lookup_arg() or self.get_lookup_field()

        operation_data = self.get_lookup_operation_data()

        assert lookup_arg in operation_data, (
            "Expected resolver %s to be called with an argument "
            'named "%s". Fix your query arguments, or set the `.lookup_field` '
            "attribute on the resolver correctly." % (self.__class__.__name__, lookup_arg)
        )
        return {self.get_lookup_field(): operation_data[lookup_arg]}

    def get_object(self):
        """
        Returns a singular object as configured by the resolver

        You may want to override this if you need to provide non-standard
        queryset lookups. Eg if objects are referenced using multiple
        arguments.
        """
        queryset = self.get_queryset()

        filter_kwargs = self.get_lookup_filter_kwargs()

        try:
            obj = queryset.get(**filter_kwargs)
        except queryset.model.DoesNotExist:
            raise exceptions.NotFoundException()

        # TODO: handle no object found for field, raise exception that always is caught and returns null for field?

        # May raise a permission denied
        if obj:
            self.check_object_permissions(self.request, obj)

        return obj

    # TODO: move out into its own mixin?
    def retrieve(self, parent, *args, **kwargs):
        return self.get_object()


class UpdateModelMixin(DetailModelMixin):
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=self.get_input_data(), partial=partial)
        valid = serializer.is_valid(raise_exception=False)

        if valid:
            instance = self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return dict(success=valid, object=instance, errors=serializer.errors)

    def perform_update(self, serializer):
        return serializer.save()

    def partial_update(self, request, *args, **kwargs):
        """
        Resolver method to use when you want to configure the serializer for partial updates
        """
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class DestroyModelMixin(DetailModelMixin):
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
