"""Tests the worldbody module."""

from pet_physics.data_model.modeling.mjcf.worldbody import Worldbody


def test_worldbody_to_xml_string():
    """Tests whether a `Worldbody` instance is correctly converted."""
    worldbody = Worldbody()

    assert worldbody.to_xml_string() == "<worldbody />"
