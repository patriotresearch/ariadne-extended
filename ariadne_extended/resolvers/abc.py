from functools import update_wrapper

import humps.main as humps
from django.utils.decorators import classonlymethod

from . import exceptions


class Resolver:
    permission_classes = []
    throttle_classes = []
    authentication_classes = []
    default_method = "retrieve"

    def __init__(self, parent, info, *operation_args, config=dict(), **operation_kwargs):
        # config is used for this specific operation on the resolver
        self.config = config.copy()
        # Graphql info object stored for access
        self.info = info
        # Get request from graphql info by default
        self.request = self.get_request(info)
        # Store parent for access
        self.parent = parent

        # Store unprocessed resolver args and kwargs
        self._operation_args = operation_args
        self._operation_kwargs = operation_kwargs

        # process resolver args and kwargs if needed
        self.operation_args = self.get_operation_args()
        self.operation_kwargs = self.get_operation_kwargs()

        # normalize federation reference args from ariadne
        self.reference_kwargs = self.get_reference_kwargs()

    def get_request(self, info):
        context = getattr(info, "context", {})
        return context.get("request", None)

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the operation handler
        """
        self.perform_authentication(request)
        self.check_permissions(request)
        self.check_throttles(request)

    def resolve(self, parent, *args, **kwargs):
        """
        Run initial checks, then call the default or configured operation resolve handler
        """
        self.initial(self.request, *args, **kwargs)

        method = self.config.get("method", self.default_method)
        handler = getattr(self, method)
        try:
            return handler(parent, *args, **kwargs)
        except exceptions.ResolverException:
            # TODO: tac on graphql errors?
            return None

    def get_operation_args(self):
        return self._operation_args

    def get_operation_kwargs(self):
        op_values = self._operation_kwargs.copy()

        # convert camelcase to snake case on all
        return humps.decamelize(op_values)

    def get_reference_kwargs(self):
        if self.config.get("reference", False):
            return humps.decamelize(self.parent)
        else:
            return dict()

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {"request": self.request, "format": None, "view": self}

    @classonlymethod
    def as_resolver(cls, **resolver_config):
        def resolver(parent, info, *args, **kwargs):
            self = cls(parent, info, config=resolver_config, *args, **kwargs)
            return self.resolve(parent, *self.operation_args, **self.operation_kwargs)

        resolver.resolver_class = cls

        # take name and docstring from class
        update_wrapper(resolver, cls, updated=())

        # and possible attributes set by decorators
        update_wrapper(resolver, cls.resolve, assigned=())

        return resolver

    @classonlymethod
    def as_nested_resolver(cls, **resolver_config):
        """
        When resolving a related type within another type. Performs needed config changes
        to trigger nested filtering between related objects and select the correct relational field
        from the orm when used inside a GenericModelResolver
        """
        resolver_config["nested"] = True
        return cls.as_resolver(**resolver_config)

    @classonlymethod
    def as_reference_resolver(cls, **resolver_config):
        """
        When resolving via reference this enables the resolver to grab the correct reference
        parameters from ariadne and utilize them in subsequent object lookups.
        """
        resolver_config["reference"] = True
        return cls.as_resolver(**resolver_config)

    def permission_denied(self, request, message=None):
        """
        If resolution is not permitted, determine what kind of exception to raise.
        """
        raise exceptions.PermissionDenied(message)

    def check_object_permissions(self, request, obj):
        """
        Check if the resolution should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(request, message=getattr(permission, "message", None))

    def check_throttles(self, request):
        """
        Check if resolution should be throttled.
        Raises an appropriate exception if the resolution is throttled.
        """
        throttle_durations = [
            throttle.wait()
            for throttle in self.get_throttles()
            if not throttle.allow_request(request, self)
        ]

        if throttle_durations:
            # Filter out `None` values which may happen in case of config / rate
            # changes, see #1438
            durations = [duration for duration in throttle_durations if duration is not None]

            duration = max(durations, default=None)
            self.throttled(self.request, duration)

    def perform_authentication(self, request):
        """
        Perform authentication on the incoming resolution.

        Note that if you override this and simply 'pass', then authentication
        will instead be performed lazily, the first time either
        `request.user` or `request.auth` is accessed.
        """
        pass

    def check_permissions(self, request):
        """
        Check if the resolution should be permitted.
        Raises an appropriate exception if the resolution is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(request, message=getattr(permission, "message", None))

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this resolver can use.
        """
        return [auth() for auth in self.authentication_classes]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this resolver requires.
        """
        return [permission() for permission in self.permission_classes]

    def get_throttles(self):
        """
        Instantiates and returns the list of throttles that this resolver uses.
        """
        return [throttle() for throttle in self.throttle_classes]

    def throttled(self, request, wait):
        """
        If request is throttled, determine what kind of exception to raise.
        """
        raise exceptions.Throttled(wait)
