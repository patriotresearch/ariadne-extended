import pytest
from ariadne import QueryType, make_executable_schema
from ariadne_extended.cursor_pagination import RelayModelMixin
from ariadne_extended.resolvers.model import GenericModelResolver
from django.apps import apps
from graphql import graphql_sync
from model_bakery import baker

from .models import Something

config = apps.get_app_config("graph_loader")


class SomethingResolver(RelayModelMixin, GenericModelResolver):
    model = Something
    queryset = Something.objects.all()
    ordering = (
        "id",
        "name",
    )


@pytest.mark.django_db
def test_connection_interface(mocker):

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

    resolvers = [
        query,
    ]

    schema = make_executable_schema(
        config.type_defs + [type_defs], config.all_app_types + resolvers
    )

    for i in range(20):
        baker.make(Something, name="st%s" % i)

    result = graphql_sync(
        schema,
        """
            query {
                things(first: 5) {
                    pageInfo {
                        hasNextPage
                        hasPreviousPage
                        startCursor
                        endCursor
                        count
                    }
                    edges {
                        cursor
                        node {
                            id
                            ... on Something {
                                name
                            }
                        }
                    }
                }
            }
        """,
    )
    assert result.errors is None
    assert result.data == dict(
        things=dict(
            pageInfo=dict(
                hasNextPage=True,
                hasPreviousPage=False,
                startCursor="MXxzdDA=",
                endCursor="NXxzdDQ=",
                count=20,
            ),
            edges=[
                dict(cursor="MXxzdDA=", node=dict(id="1", name="st0")),
                dict(cursor="MnxzdDE=", node=dict(id="2", name="st1")),
                dict(cursor="M3xzdDI=", node=dict(id="3", name="st2")),
                dict(cursor="NHxzdDM=", node=dict(id="4", name="st3")),
                dict(cursor="NXxzdDQ=", node=dict(id="5", name="st4")),
            ],
        )
    )
