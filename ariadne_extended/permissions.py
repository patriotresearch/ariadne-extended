"""
Provides a set of pluggable permission policies.
"""


class OperationHolderMixin:
    def __and__(self, other):
        return OperandHolder(AND, self, other)

    def __or__(self, other):
        return OperandHolder(OR, self, other)

    def __rand__(self, other):
        return OperandHolder(AND, other, self)

    def __ror__(self, other):
        return OperandHolder(OR, other, self)

    def __invert__(self):
        return SingleOperandHolder(NOT, self)

    def __eq__(self, other) -> bool:
        if not hasattr(self, "op1_class"):
            return self is other
        if hasattr(self, "op2_class"):
            return self.op1_class is other.op1_class and self.op2_class is other.op2_class
        else:
            return self.op1_class is other.op1_class


class SingleOperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class):
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        return self.operator_class(op1)


class OperandHolder(OperationHolderMixin):
    def __init__(self, operator_class, op1_class, op2_class):
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)


class AND:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, request, resolver):
        return self.op1.has_permission(request, resolver) and self.op2.has_permission(
            request, resolver
        )

    def has_object_permission(self, request, resolver, obj):
        return self.op1.has_object_permission(
            request, resolver, obj
        ) and self.op2.has_object_permission(request, resolver, obj)


class OR:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, request, resolver):
        return self.op1.has_permission(request, resolver) or self.op2.has_permission(
            request, resolver
        )

    def has_object_permission(self, request, resolver, obj):
        return self.op1.has_object_permission(
            request, resolver, obj
        ) or self.op2.has_object_permission(request, resolver, obj)


class NOT:
    def __init__(self, op1):
        self.op1 = op1

    def has_permission(self, request, resolver):
        return not self.op1.has_permission(request, resolver)

    def has_object_permission(self, request, resolver, obj):
        return not self.op1.has_object_permission(request, resolver, obj)


class BasePermissionMetaclass(OperationHolderMixin, type):
    pass


class BasePermission(metaclass=BasePermissionMetaclass):
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, request, resolver):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def has_object_permission(self, request, resolver, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True


class AllowAny(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self, request, resolver):
        return True


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, resolver):
        return bool(request.user and request.user.is_authenticated)


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, resolver):
        return bool(request.user and request.user.is_staff)
