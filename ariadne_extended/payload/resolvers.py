from copy import copy

import humps.main as humps
from ariadne import FallbackResolversSetter
from graphql.type import GraphQLList, GraphQLField
from .types import error_detail, payload
from rest_framework.exceptions import ErrorDetail


@error_detail.field("error")
def resolve_error_detail_error(parent, info, *args, **kwargs):
    """Cast the error as a string to retrieve the message"""
    return str(parent)


def traverse_errors(fields, node, stack=""):

    # Does the list contain errors or more fields?
    if isinstance(node, list):
        if any([isinstance(i, ErrorDetail) for i in node]):
            stack_key = copy(stack)
            fields.append(dict(name=humps.camelize(stack_key), values=node))
        else:
            for i, item in enumerate(node):
                # if item is an empty dict, stop.
                if item == {}:
                    continue
                stack_key = copy(stack)
                stack_key = f"{stack_key}[{i}]"
                traverse_errors(fields, item, stack_key)

    # If node is a dict, use the keys
    if isinstance(node, dict):
        for name, errors in node.items():
            # Copy key so the ref is lost and the chain becomes unique
            stack_key = copy(stack)
            if bool(stack_key):
                if isinstance(name, int):
                    stack_key = f"{stack_key}[{name}]"
                else:
                    stack_key = f"{stack_key}.{name}"
            else:
                stack_key = name
            traverse_errors(fields, errors, stack=stack_key)


@payload.field("errors")
def resolve_payload_errors(parent, info, *args, **kwargs):
    fields = list()
    traverse_errors(fields, parent["errors"])
    return fields
