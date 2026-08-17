"""Tests that belong to the module `body_max_contact_force_top`."""

from pet_physics.data_model.evaluation.forces.body_max_contact_force_top import BodyMaxContactForceTop
from pet_physics.data_model.serialization import to_dict


def test_serialization() -> None:
    """Tests whether the serialization of a `BodyMaxContactForceTop` object correctly works."""
    body_max_contact_force_top = BodyMaxContactForceTop(name="body_pi", max_contact_force_top=3.14159265)

    EXPECTED_DICT = {"name": "body_pi", "max_contact_force_top": 3.14159265}

    assert to_dict(body_max_contact_force_top) == EXPECTED_DICT
