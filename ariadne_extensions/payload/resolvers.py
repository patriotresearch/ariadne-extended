from copy import copy

import humps.main as humps
from ariadne import FallbackResolversSetter
from graphql.type import GraphQLList, GraphQLField
from .types import error_detail

__resolvers__ = ["field_error_resolver"]


@error_detail.field("error")
def resolve_error_detail_error(parent, info, *args, **kwargs):
    """Cast the error as a string to retrieve the message"""
    return str(parent)


def resolve_field_errors(parent, info, *args, **kwargs):
    fields = list()

    def traverse(node, stack=""):
        for name, errors in node.items():
            inner_stack = copy(stack)
            if bool(inner_stack):
                if isinstance(name, int):
                    inner_stack = f"{inner_stack}[{name}]"
                else:
                    inner_stack = f"{inner_stack}.{name}"
            else:
                inner_stack = name

            if isinstance(errors, list):
                # final condition
                fields.append(dict(name=humps.camelize(inner_stack), values=errors))
            else:
                traverse(errors, stack=inner_stack)

    traverse(parent["errors"])
    return fields


class CustomFieldErrorResolver(FallbackResolversSetter):
    def add_resolver_to_field(self, name: str, field_object: GraphQLField) -> None:
        if field_object.resolve is None and name == "errors":
            if (
                isinstance(field_object.type, GraphQLList)
                and field_object.type.of_type.name == "FieldError"
            ):
                field_object.resolve = resolve_field_errors


field_error_resolver = CustomFieldErrorResolver()
