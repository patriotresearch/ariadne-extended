from ariadne_extended.resolvers import exceptions
from django.contrib.admin.options import get_content_type_for_model
from django.db import models

from ..filters import FilterMixin
from .abc import Resolver
from .mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class GenericModelResolver(Resolver):
    """
    Model based resolver based off of DRF model views.
    """

    queryset = None
    model = None
    nested_field_name = None
    lookup_arg = None
    lookup_field = "id"

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, models.query.QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        if self.config.get("nested", False):
            queryset = self.filter_nested_queryset(queryset).all()
        return queryset

    def get_model(self):
        if self.model is not None:
            return self.model
        else:
            return self.get_queryset().model

    def filter_nested_queryset(self, queryset):
        # see if we can just use the info context and the name of the resolver field
        # to reverse the relation, fallback on parent_name
        try:
            return getattr(
                self.parent,
                self.config.get("nested_field_name", self.nested_field_name)
                or self.info.field_name,
            )
        except AttributeError:
            params = {}
            if self.config.get("parent_name", None) == "object_id":
                params["object_id"] = self.parent.id
                params["content_type"] = get_content_type_for_model(self.parent._meta.model)
            elif self.config.get("parent_name", None):
                params[self.config.get("parent_name")] = self.parent.id

            return queryset.filter(**params)

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

        # May raise a permission denied exception
        if obj:
            self.check_object_permissions(self.request, obj)

        return obj


class ModelResolver(
    RetrieveModelMixin,
    CreateModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    FilterMixin,
    GenericModelResolver,
):
    default_method = "retrieve"


class ListModelResolver(ListModelMixin, GenericModelResolver):
    pass
