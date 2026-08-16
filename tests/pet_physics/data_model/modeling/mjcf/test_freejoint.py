"""Tests the freejoint module."""

from pet_physics.data_model.modeling.mjcf.freejoint import Freejoint


def test_freejoint_to_xml_string():
    """Tests whether a `Freejoint` instance is correctly converted."""
    expected_xml_string = "<freejoint />"
    assert Freejoint().to_xml_string() == expected_xml_string
