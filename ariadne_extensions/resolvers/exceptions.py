from django.utils.translation import ugettext_lazy as _


class ResolverException(Exception):
    pass


class PermissionDenied(ResolverException):
    default_detail = _("You do not have permission to query this field.")
    default_code = "permission_denied"
