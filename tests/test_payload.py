from rest_framework.exceptions import ErrorDetail

from ariadne_extended.payload.resolvers import resolve_field_errors


def test_resolve_field_errors_basic():
    error_struct = dict(errors=dict(field_one=[ErrorDetail("An error", code=123)]))

    result = resolve_field_errors(error_struct, None)
    assert result == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)])
    ], "Single fields just include their name"


def test_resolve_field_errors_nested():
    nested_error_struct = dict(
        errors=dict(
            field_one=[ErrorDetail("An error", code=123)],
            field_two=dict(nested_field=[ErrorDetail("An error", code=123)]),
        )
    )

    result = resolve_field_errors(nested_error_struct, None)
    assert result == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)]),
        dict(name="fieldTwo.nestedField", values=[ErrorDetail("An error", code=123)]),
    ], "Nested fields use dot lookup notation"


def test_resolve_field_errors_nested_index():
    nested_index_error_struct = dict(
        errors=dict(
            field_one=[ErrorDetail("An error", code=123)],
            field_two={0: [ErrorDetail("An error", code=123)]},
        )
    )

    result = resolve_field_errors(nested_index_error_struct, None)
    assert result == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)]),
        dict(name="fieldTwo[0]", values=[ErrorDetail("An error", code=123)]),
    ], "Indexed errors use array lookup notation"


def test_resolve_field_errors_nested_index_object():
    nested_index_error_object_struct = dict(
        errors=dict(
            field_one=[ErrorDetail("An error", code=123)],
            field_two={0: dict(nested_field=[ErrorDetail("An error", code=123)])},
        )
    )

    result = resolve_field_errors(nested_index_error_object_struct, None)
    assert result == [
        dict(name="fieldOne", values=[ErrorDetail("An error", code=123)]),
        dict(name="fieldTwo[0].nestedField", values=[ErrorDetail("An error", code=123)]),
    ], "Indexed errors can have nested fields"
