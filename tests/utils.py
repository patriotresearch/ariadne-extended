from ariadne import graphql_sync
from ariadne.format_error import format_error
from model_bakery import baker
from unittest.mock import Mock
from django.conf import settings
import pytest


def assert_no_errors(result):
    if result.get("errors", None):
        for error in result.get("errors", None):
            formatted = format_error(error, True)
            print(formatted.get("extensions").get("exception").get("stacktrace"))
    assert result.get("errors", None) is None


@pytest.mark.django_db
def run_graphql(schema, gql, request_user=None, addition_context=dict(), **kwargs):
    if request_user is None:
        request_user = baker.make(settings.AUTH_USER_MODEL)

    request = Mock("MockRequest")
    request.user = request_user
    context = dict(request=request, **addition_context)

    success, result = graphql_sync(schema, gql, context_value=context, **kwargs)
    return result
