from rest_framework.exceptions import ErrorDetail

from ariadne_extended.payload.resolvers import traverse_errors


def test_traverse_errors_basic():
    error_struct = dict(field_one=[ErrorDetail("An error", code=123)])

    fields = list()
    traverse_errors(fields, error_struct, None)
    assert fields == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)])
    ], "Single fields just include their name"


def test_traverse_errors_nested():
    nested_error_struct = dict(
        field_one=[ErrorDetail("An error", code=123)],
        field_two=dict(nested_field=[ErrorDetail("An error", code=123)]),
    )

    fields = list()
    traverse_errors(fields, nested_error_struct, None)
    assert fields == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)]),
        dict(name="fieldTwo.nestedField", values=[ErrorDetail("An error", code=123)]),
    ], "Nested fields use dot lookup notation"


def test_traverse_errors_nested_index():
    nested_index_error_struct = dict(
        field_one=[ErrorDetail("An error", code=123)],
        field_two={0: [ErrorDetail("An error", code=123)]},
    )

    fields = list()
    traverse_errors(fields, nested_index_error_struct, None)
    assert fields == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)]),
        dict(name="fieldTwo[0]", values=[ErrorDetail("An error", code=123)]),
    ], "Indexed errors use array lookup notation"


def test_traverse_errors_nested_index_object():
    nested_index_error_object_struct = dict(
        field_one=[ErrorDetail("An error", code=123)],
        field_two={0: dict(nested_field=[ErrorDetail("An error", code=123)])},
    )

    fields = list()
    traverse_errors(fields, nested_index_error_object_struct, None)
    assert fields == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)]),
        dict(name="fieldTwo[0].nestedField", values=[ErrorDetail("An error", code=123)]),
    ], "Indexed errors can have nested fields"


def test_traverse_errors_multiple_nested():
    nested_indexed_struct = dict(fields=[{}, {}, {"title": [ErrorDetail("An error", code=123)]}])
    fields = list()
    traverse_errors(fields, nested_indexed_struct, None)
    assert fields == [
        dict(name="fields[2].title", values=[ErrorDetail("An error", code=123)])
    ], "Nested indexed errors returns one named error"


def test_traverse_errors_multiple_nested_further():
    nested_indexed_struct = dict(
        fields=[
            {},
            {},
            {
                "title": [ErrorDetail("An error", code=123)],
                "options": [{}, {"name": [ErrorDetail("Name required", code=321)]}],
            },
        ]
    )

    fields = list()
    traverse_errors(fields, nested_indexed_struct, None)
    assert fields == [
        dict(name="fields[2].title", values=[ErrorDetail("An error", code=123)]),
        dict(name="fields[2].options[1].name", values=[ErrorDetail("Name required", code=321)]),
    ], "Nested indexed errors returns deep indexed errors"
