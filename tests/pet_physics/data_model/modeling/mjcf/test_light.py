"""Tests the light module."""

from pet_physics.data_model.modeling.mjcf.light import Light


def test_light_to_xml_string():
    """Tests whether a `Light` instance is correctly converted."""
    light = Light((0.5, 0.5, 0.5), pos=(0, 0, 10), dir=(0, 0, -1))
    expected_string = '<light diffuse="0.5 0.5 0.5" pos="0 0 10" dir="0 0 -1" />'

    assert light.to_xml_string() == expected_string
