from enum import Enum

import pytest
from ariadne import make_executable_schema
from django.apps import apps
from glom import Path, glom
from graphql import graphql_sync
from model_bakery import baker
from waffle import get_waffle_flag_model
from waffle.models import Sample, Switch


config = apps.get_app_config("graph_loader")


@pytest.mark.django_db
def test_enum_input_value_resolution(mocker):

    # Add test example flags, switches and samples
    type_defs = """
        type Query
    """

    schema = make_executable_schema(config.type_defs + [type_defs], config.all_app_types)

    for i in range(2):
        baker.make(get_waffle_flag_model(), name="flag%s" % i, everyone=bool(i % 2), note="a flag")

    for i in range(2):
        baker.make(Switch, name="switch%s" % i, active=bool(i % 2), note="a switch")

    for i in range(2):
        baker.make(Sample, name="sample%s" % i, percent="100", note="a sample")

    result = graphql_sync(
        schema,
        """
        query {
            waffle {
                flags {
                    ...BaseWaffleItem
                }
                switches {
                    ...BaseWaffleItem
                }
                samples {
                    ...BaseWaffleItem
                }
                all {
                    ...BaseWaffleItem
                }
                flagDefault
                switchDefault
                sampleDefault
            }
        }
        fragment BaseWaffleItem on WaffleItem {
            __typename
            id
            name
            active
            note
        }
        """,
    )
    assert result.errors is None
    waffle = result.data.get("waffle")

    assert glom(waffle, "flags.0.active") == False
    assert glom(waffle, "flags.1.active") == True
    assert glom(waffle, "switches.0.active") == False
    assert glom(waffle, "switches.1.active") == True
    assert glom(waffle, "samples.0.active") == True
    assert glom(waffle, "samples.1.active") == True

    assert glom(waffle, "flags.0.name") == "flag0"
    assert glom(waffle, "flags.1.name") == "flag1"

    assert glom(waffle, "flagDefault") == False
    assert glom(waffle, "switchDefault") == False
    assert glom(waffle, "sampleDefault") == True
