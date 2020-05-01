from enum import Enum

import pytest
from ariadne import EnumType, QueryType, make_executable_schema
from ariadne_extended.resolvers import Resolver
from ariadne_extended.resolvers.mixins import InputMixin
from glom import glom
from graphql import graphql, graphql_sync
from graphql.utilities import strip_ignored_characters as sic
from graphql.utilities.schema_printer import print_interface, print_object, print_union


def test_input_mixin_attrs():
    assert InputMixin.input_arg == "input"
    assert InputMixin.convert_enums == True


def test_input_mixin_get_input_arg():
    class AlteredInputMixin(InputMixin):
        input_arg = "another_input"

    arg = InputMixin().get_input_arg()
    assert arg == "input"

    arg = AlteredInputMixin().get_input_arg()
    assert arg == "another_input"


def test_enum_input_value_resolution(mocker):
    class ClownTypes(Enum):
        SAD = "Sad Clown"
        HAPPY = "Happy Clown"

    class ClownEmotionResolver(InputMixin, Resolver):
        def retrieve(self, *args, **kwargs):
            """Get sad, return happy"""
            assert self.get_input_data().get("type") == "Sad Clown"
            return ClownTypes.HAPPY

    class ClownEmotionResolverOff(InputMixin, Resolver):
        convert_enums = False

        def retrieve(self, *args, **kwargs):
            """Get sad enum, return happy enum"""
            assert self.get_input_data().get("type") == ClownTypes.SAD
            return ClownTypes.HAPPY

    type_defs = """
        enum ClownTypes {
            "Sad Clown"
            SAD
            "Happy Clown"
            HAPPY
        }

        input ClownInput {
            type: ClownTypes
        }

        type Query {
            clownEmotion(input: ClownInput!): ClownTypes
            clownEmotionOff(input: ClownInput!): ClownTypes
        }
    """

    query = QueryType()

    clown_types = EnumType("ClownTypes", ClownTypes)

    query.set_field("clownEmotion", ClownEmotionResolver.as_resolver())
    query.set_field("clownEmotionOff", ClownEmotionResolverOff.as_resolver())

    resolvers = [query, clown_types]

    schema = make_executable_schema(type_defs, resolvers)

    result = graphql_sync(
        schema,
        """
            query {
                on: clownEmotion(input: {type: SAD})
                off: clownEmotionOff(input: {type: SAD})
            }
        """
    )
    assert result.errors is None
    assert glom(result.data, "on") == "HAPPY"
    assert glom(result.data, "off") == "HAPPY"
