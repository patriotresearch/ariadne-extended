from ariadne import snake_case_fallback_resolvers
from ariadne.contrib.django.scalars import date_scalar, datetime_scalar
from ariadne.contrib.federation import make_federated_schema
from django.apps import apps

from .resolvers import field_error_resolvers, page_info_resolvers

config = apps.get_app_config("graph_loader")


# TODO: not used
# schema = make_federated_schema(
#     config.type_defs,
#     config.types
#     + [
#         page_info_resolvers,
#         field_error_resolvers,
#         snake_case_fallback_resolvers,
#         datetime_scalar,
#         date_scalar,
#     ],
# )
