"""Tests that belong to the module `result_evaluator_max_contact_force_top`."""

from pet_physics.data_model.evaluation.forces.body_max_contact_force_top import BodyMaxContactForceTop
from pet_physics.data_model.evaluation.forces.result_evaluator_max_contact_force_top import (
    ResultEvaluatorMaxContactForceTop,
)
from pet_physics.data_model.serialization import to_dict


def test_serialization() -> None:
    """Tests whether the serialization of a `ResultEvaluatorMaxContactForceTop` object correctly works."""
    record_1 = BodyMaxContactForceTop(name="body_pi", max_contact_force_top=3.14159265)

    result = ResultEvaluatorMaxContactForceTop()
    result.add(record=record_1)
    EXPECTED_DICT = {"body_pi": 3.14159265}

    assert to_dict(result) == EXPECTED_DICT

    record_2 = BodyMaxContactForceTop(name="body_42", max_contact_force_top=42)
    result.add(record=record_2)
    EXPECTED_DICT = {"body_pi": 3.14159265, "body_42": 42}

    assert to_dict(result) == EXPECTED_DICT
