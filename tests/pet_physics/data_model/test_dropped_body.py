"""Tests for `DroppedBody`."""

from pet_physics.data_model.dropped_body import DroppedBody


def test_dropped_body_stores_name_and_drop_timestamp() -> None:
    """Constructing a `DroppedBody` should store the given name and drop timestamp."""
    dropped_body = DroppedBody(name="box_a", drop_timestamp=3)

    assert dropped_body.name == "box_a"
    assert dropped_body.drop_timestamp == 3


def test_dropped_bodies_with_equal_fields_compare_equal() -> None:
    """Two `DroppedBody` instances with the same field values should be equal."""
    assert DroppedBody(name="box_a", drop_timestamp=1.5) == DroppedBody(name="box_a", drop_timestamp=1.5)


def test_dropped_bodies_with_different_fields_are_not_equal() -> None:
    """`DroppedBody` instances with differing field values should not be equal."""
    assert DroppedBody(name="box_a", drop_timestamp=1) != DroppedBody(name="box_b", drop_timestamp=1)
