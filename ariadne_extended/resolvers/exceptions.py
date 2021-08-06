from django.utils.translation import gettext_lazy as _


class ResolverException(Exception):
    def __init__(self, message, info=None, resolver=None):
        super().__init__(message, info, resolver)
        self.message = message
        self.info = info
        self.resolver = resolver

    def __str__(self):
        if hasattr(self, "info"):
            return f"{self.message} {repr(self.resolver)} {repr(self.info)}"
        return self.message

    def __repr__(self):
        return "%s(%s)" % self.__class__.__name__, self


class NotFoundException(ResolverException):
    pass


class PermissionDenied(ResolverException):
    pass


class Throttled(ResolverException):
    pass
