from django.contrib.admin.options import get_content_type_for_model
from django.db import models

from ..filters import FilterMixin
from .abc import Resolver
from .mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)


class GenericModelResolver(Resolver):
    """
    Model based resolver based off of DRF model views.
    """

    queryset = None
    model = None
    nested_field_name = None

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


class ModelResolver(
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin, FilterMixin, GenericModelResolver
):
    pass


class ListModelResolver(ListModelMixin, GenericModelResolver):
    pass
