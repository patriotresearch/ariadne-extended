from ariadne import InterfaceType, ObjectType
from django.db import models


page_info = ObjectType("PageInfo")


node = InterfaceType("Node")


def resolve_node_type(obj, *args):
    if isinstance(obj, models.Model):
        gtype = getattr(obj, "graphql_type", None)
        if isinstance(gtype, str):
            return gtype
        return obj.__class__.__name__


node.set_type_resolver(resolve_node_type)
