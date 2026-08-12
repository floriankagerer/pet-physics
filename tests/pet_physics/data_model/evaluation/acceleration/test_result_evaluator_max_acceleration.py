"""Tests that belong to the module `result_evaluator_max_acceleration`."""

from pet_physics.data_model.evaluation.acceleration.body_max_acceleration import BodyMaxAcceleration
from pet_physics.data_model.evaluation.acceleration.result_evaluator_max_acceleration import (
    ResultEvaluatorMaxAcceleration,
)
from pet_physics.data_model.serialization import to_dict


def test_serialization() -> None:
    """Tests whether the serialization of a `ResultEvaluatorMaxAcceleration` object correctly works."""
    record = BodyMaxAcceleration(name="test", max_linear_acceleration=42.0, max_angular_acceleration=3.14159265)

    result = ResultEvaluatorMaxAcceleration()
    result.add(record=record)

    EXPECTED_DICT = {"test": {"name": "test", "max_linear_acceleration": 42.0, "max_angular_acceleration": 3.14159265}}

    assert to_dict(result) == EXPECTED_DICT


def test_properties() -> None:
    """Tests whether the properties of an object are correctly returned."""
    record_max_linear = BodyMaxAcceleration(name="body_1", max_linear_acceleration=42.0, max_angular_acceleration=1)
    record_max_angular = BodyMaxAcceleration(name="body_2", max_linear_acceleration=2, max_angular_acceleration=3.1415)

    result = ResultEvaluatorMaxAcceleration()
    result.add(record=record_max_linear).add(record=record_max_angular)

    assert result.maximal_value_linear_acceleration == record_max_linear.max_linear_acceleration
    assert result.maximal_value_angular_acceleration == record_max_angular.max_angular_acceleration
