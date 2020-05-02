from enum import Enum

import pytest
from ariadne import EnumType, QueryType, make_executable_schema
from ariadne_extended.cursor_pagination import RelayModelMixin
from ariadne_extended.resolvers.model import GenericModelResolver
from glom import glom
from graphql import  graphql_sync
from django.apps import apps
from model_bakery import baker


config = apps.get_app_config("graph_loader")


from .models import Something


class SomethingResolver(RelayModelMixin, GenericModelResolver):
    model = Something
    queryset = Something.objects.all()
    ordering = ("id", "name",)

@pytest.mark.django_db
def test_enum_input_value_resolution(mocker):

    type_defs = """
        type Something implements Node {
            id: ID!
            name: String
        }
        type SomethingElse implements Node {
            id: ID!
            else: Boolean
        }
        type Query {
            things(first: Int, last: Int, after: String, before: String): Connection
        }
    """


    query = QueryType()

    query.set_field("things", SomethingResolver.as_resolver(method="list"))

    resolvers = [query,]

    schema = make_executable_schema(
        config.type_defs + [type_defs],
        config.all_app_types + resolvers
    )

    for i in range(20):
        baker.make(Something, name="st%s" % i)

    result = graphql_sync(
        schema,
        """
            query {
                things(first: 5) {
                    edges {
                        cursor
                        node {
                            __typename
                            id
                            ... on Something {
                                name
                            }
                        }
                    }
                }
            }
        """
    )
    assert result.errors is None
    # assert glom(result.data, "things[0].node.name") == "st0"
