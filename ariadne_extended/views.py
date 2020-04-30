import json
from typing import Optional, cast

from ariadne.contrib.django.views import GraphQLView
from ariadne.contrib.tracing.apollotracing import ApolloTracingExtensionSync
from ariadne.format_error import format_error
from ariadne.graphql import graphql_sync
from ariadne.types import ContextValue, ErrorFormatter, GraphQLResult, RootValue
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from graphql import GraphQLSchema
from graphql import format_error as format_graphql_error
from graphql.error import GraphQLError
from graphql.execution import MiddlewareManager


@method_decorator(csrf_exempt, name="dispatch")
class BaseGraphQLView(GraphQLView):
    extensions = [ApolloTracingExtensionSync]

    def execute_query(self, request: HttpRequest, data: dict) -> GraphQLResult:
        """TODO: remove when extensions is added to graphql_sync in parent view"""
        if callable(self.context_value):
            context_value = self.context_value(request)  # pylint: disable=not-callable
        else:
            context_value = self.context_value or request

        return graphql_sync(
            cast(GraphQLSchema, self.schema),
            data,
            context_value=context_value,
            root_value=self.root_value,
            validation_rules=self.validation_rules,
            debug=settings.DEBUG,
            logger=self.logger,
            error_formatter=self.error_formatter or format_error,
            extensions=self.extensions,
            middleware=self.middleware,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LoginRequiredGraphQLView(LoginRequiredMixin, BaseGraphQLView):
    def handle_no_permission(self):
        return HttpResponseForbidden()


class HttpError(Exception):
    def __init__(self, response, message=None, *args, **kwargs):
        self.response = response
        self.message = message = message or response.content.decode()
        super(HttpError, self).__init__(message, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class BatchGraphQLView(LoginRequiredMixin, View):
    """
    Batch GraphQL view based on the graphene batch view.
    """

    # FIX: GraphQL errors aren't bubbling up properly, probably due to the differences with Graphene
    http_method_names = ["get", "post", "options"]
    schema: Optional[GraphQLSchema] = None
    context_value: Optional[ContextValue] = None
    root_value: Optional[RootValue] = None
    logger = None
    validation_rules = None
    error_formatter: Optional[ErrorFormatter] = None
    middleware: Optional[MiddlewareManager] = None
    batch = False
    pretty = False

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.handle_query(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        return self.handle_query(request, *args, **kwargs)

    def handle_query(self, request, *args, **kwargs):
        if not self.schema:
            raise ValueError("GraphQLView was initialized without schema.")
        try:
            data = self.extract_data_from_request(request)

            if self.batch:
                responses = [self.get_response(request, entry) for entry in data]
                result = "[{}]".format(",".join([response[0] for response in responses]))
                status_code = (
                    responses and max(responses, key=lambda response: response[1])[1] or 200
                )
            else:
                result, status_code = self.get_response(request, data)

            return HttpResponse(
                status=status_code, content=result, content_type="application/json"
            )

        except HttpError as e:
            # TODO: return actual JsonResponse
            response = e.response
            response["Content-Type"] = "application/json"
            response.content = self.json_encode(request, {"errors": [self.format_error(e)]})
            return response

    def get_response(self, request, data):
        params = self.get_graphql_params(request, data)

        execution_result_passed, execution_result = self.execute_graphql_request(request, params)

        status_code = 200
        response = {}
        if execution_result_passed:
            if execution_result.get("errors", False):
                status_code = 400
            else:
                response["data"] = execution_result["data"]

        else:
            status_code = 400
            response["errors"] = [self.format_error(e) for e in execution_result["errors"]]

        if self.batch:
            response["id"] = params["id"]
            response["status"] = status_code

        result = self.json_encode(request, response)
        return result, status_code

    def extract_data_from_request(self, request):
        content_type = self.get_content_type(request)

        if content_type == "application/graphql":
            return {"query": request.body.decode()}

        elif content_type == "application/json":
            # noinspection PyBroadException
            try:
                body = request.body.decode("utf-8")
            except Exception as e:
                raise HttpError(HttpResponseBadRequest(str(e)))

            try:
                request_json = json.loads(body)
                if self.batch:
                    assert isinstance(request_json, list), (
                        "Batch requests should receive a list, but received {}."
                    ).format(repr(request_json))
                    assert len(request_json) > 0, "Received an empty list in the batch request."
                else:
                    assert isinstance(
                        request_json, dict
                    ), "The received data is not a valid JSON query."
                return request_json
            except AssertionError as e:
                raise HttpError(HttpResponseBadRequest(str(e)))
            except (TypeError, ValueError):
                raise HttpError(HttpResponseBadRequest("POST body sent invalid JSON."))

        elif content_type in ["application/x-www-form-urlencoded", "multipart/form-data"]:
            return request.POST

        return {}

    def execute_graphql_request(self, request, data):
        if callable(self.context_value):
            context_value = self.context_value(request)
        else:
            context_value = self.context_value or request

        return graphql_sync(
            cast(GraphQLSchema, self.schema),
            data,
            context_value=context_value,
            root_value=self.root_value,
            debug=settings.DEBUG,
            logger=self.logger,
            validation_rules=self.validation_rules,
            error_formatter=self.error_formatter or format_error,
            middleware=self.middleware,
        )

    @staticmethod
    def get_graphql_params(request, data):
        query = request.GET.get("query") or data.get("query")
        variables = request.GET.get("variables") or data.get("variables")
        id = request.GET.get("id") or data.get("id")

        if variables and isinstance(variables, str):
            try:
                variables = json.loads(variables)
            except Exception:
                raise HttpError(HttpResponseBadRequest("Variables are invalid JSON."))

        operation_name = request.GET.get("operationName") or data.get("operationName")
        if operation_name == "null":
            operation_name = None

        return dict(query=query, variables=variables, operation_name=operation_name, id=id)

    @staticmethod
    def format_error(error):
        if isinstance(error, GraphQLError):
            return format_graphql_error(error)

        return {"message": str(error)}

    @staticmethod
    def get_content_type(request):
        meta = request.META
        content_type = meta.get("CONTENT_TYPE", meta.get("HTTP_CONTENT_TYPE", ""))
        return content_type.split(";", 1)[0].lower()

    def json_encode(self, request, data, pretty=False):
        if not (self.pretty or pretty) and not request.GET.get("pretty"):
            return json.dumps(data, separators=(",", ":"))

        return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": "))
