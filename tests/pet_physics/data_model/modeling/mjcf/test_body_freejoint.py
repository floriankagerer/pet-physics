"""Tests for the freejoint body module."""

from pet_physics.data_model.modeling.mjcf.body_freejoint import BodyFreejoint


def test_body_freejoint_to_xml_string():
    free_body = BodyFreejoint(name="free_test", pos=(0, 0, 0))

    expected_xml_string = '<body name="free_test" pos="0 0 0"><freejoint /></body>'

    assert free_body.to_xml_string() == expected_xml_string
