"""Tests that belong to the module `body_max_acceleration`."""

from pet_physics.data_model.evaluation.acceleration.body_max_acceleration import BodyMaxAcceleration
from pet_physics.data_model.serialization import to_dict


def test_serialization() -> None:
    """Tests whether the serialization of a `BodyMaxAcceleration` object correctly works."""
    body_max_acc = BodyMaxAcceleration(name="test", max_linear_acceleration=42.0, max_angular_acceleration=3.14159265)

    EXPECTED_DICT = {"name": "test", "max_linear_acceleration": 42.0, "max_angular_acceleration": 3.14159265}

    assert to_dict(body_max_acc) == EXPECTED_DICT
