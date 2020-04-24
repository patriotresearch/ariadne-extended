"""
TODO: remove dependency on DRF field
"""
from ariadne import ScalarType

from rest_framework.fields import UUIDField


uuid_field = UUIDField()


uuid = ScalarType(
    "UUID", serializer=uuid_field.to_representation, value_parser=uuid_field.to_internal_value
)
