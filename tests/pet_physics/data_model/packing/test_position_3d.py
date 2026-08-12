"""Tests the `position_3d` module."""

import pytest

from pet_physics.data_model.packing.position_3d import Position3D


@pytest.mark.parametrize(
    "serialize_none, actual_position, expected_serialized",
    [
        (
            False,
            Position3D(x=300, y=200, z=100, area=None),
            {"x": 300, "y": 200, "z": 100},
        ),
        (
            True,
            Position3D(x=300, y=200, z=100, area=None),
            {"x": 300, "y": 200, "z": 100, "area": None},
        ),
        (
            False,
            Position3D(x=300, y=200, z=100, area="area"),
            {"x": 300, "y": 200, "z": 100, "area": "area"},
        ),
        (
            True,
            Position3D(x=300, y=200, z=100, area="area"),
            {"x": 300, "y": 200, "z": 100, "area": "area"},
        ),
    ],
)
def test_position_3d_serialization(
    serialize_none: bool, actual_position: Position3D, expected_serialized: dict
) -> None:
    """Tests whether an object of the dataclass `Position3D` is correctly serialized."""

    import pet_physics.data_model.packing.position_3d

    # Set the variable that defines whether `None` is serialized
    pet_physics.data_model.packing.position_3d.SERIALIZE_NONE = serialize_none

    assert actual_position.to_dict() == expected_serialized


@pytest.mark.parametrize(
    "serialized_position, expected_position",
    [
        (
            {"x": 300, "y": 200, "z": 100},
            Position3D(x=300, y=200, z=100, area=None),
        ),
        (
            {"x": 300, "y": 200, "z": 100, "area": "area"},
            Position3D(x=300, y=200, z=100, area="area"),
        ),
    ],
)
def test_position_3d_deserialization(serialized_position: dict, expected_position: Position3D) -> None:
    """Tests whether we correctly deserialize."""
    deserialized = Position3D.from_dict(serialized_position)

    assert deserialized == expected_position


def test_position_3d_xyz() -> None:
    """Tests whether the property `xyz` is correctly returned."""
    position = Position3D(x=600, y=400, z=200, area=None)

    assert isinstance(position.xyz, tuple)
    assert position.xyz == (600, 400, 200)
