"""Tests the mujoco model module."""

from pet_physics.data_model.modeling.mjcf.mujoco_model import MuJoCoModel


def test_mujoco_model_to_xml_string():
    """Tests whether a `MuJoCoModel` is correctly converted."""
    mujoco_model = MuJoCoModel(model="test")
    expected_xml_string = '<mujoco model="test" />'

    assert mujoco_model.to_xml_string() == expected_xml_string
