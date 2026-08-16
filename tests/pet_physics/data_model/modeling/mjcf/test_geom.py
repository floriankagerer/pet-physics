"""Tests the geom module."""

from pet_physics.data_model.modeling.mjcf.geom import Geom


def test_geom_to_xml_string():
    """Tests whether a `Geom` instance is correctly converted."""
    yellow_box_geom = Geom(
        name="yellow_box",
        type="box",
        size=(0.1, 0.1, 0.1),
        rgba=(1, 1, 0, 1),
        mass=1.0,
        pos=None,
        solimp=(0.99, 0.99, 0.01),
        solref=(0.001, 1),
        mesh=None,
        material=None,
        friction=(1.0, 0.005, 0.0001),
        gap=None,
    )

    expected_xml_string = '<geom name="yellow_box" type="box" size="0.1 0.1 0.1" mass="1.0" rgba="1 1 0 1" solimp="0.99 0.99 0.01" solref="0.001 1" friction="1.0 0.005 0.0001" />'

    assert yellow_box_geom.to_xml_string() == expected_xml_string
