from django.utils.translation import gettext_lazy as _


class ResolverException(Exception):
    pass


class NotFoundException(ResolverException):
    pass


class PermissionDenied(ResolverException):
    default_detail = _("You do not have permission to query this field.")
    default_code = "permission_denied"


class Throttled(ResolverException):
    pass
