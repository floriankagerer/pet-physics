import pytest

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.geom import Geom


def test_body_to_xml_string():
    """Tests whether the constructor of the data class `Body` works as expected."""
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
    exp_geom_xml_string = """<geom name="yellow_box" type="box" size="0.1 0.1 0.1" mass="1.0" rgba="1 1 0 1" solimp="0.99 0.99 0.01" solref="0.001 1" friction="1.0 0.005 0.0001" />"""
    top_box = Body(
        name="top_box",
        pos=(0, 0, 0.4),
    )
    top_box.add_child(yellow_box_geom)

    expected_xml_string = f"""<body name="top_box" pos="0 0 0.4">{exp_geom_xml_string}</body>"""

    assert top_box.to_xml_string() == expected_xml_string


def test_body_property_geom():
    """Tests whether the property `geom` works as expected, i.e, either returning the `Geom` child or raising an
    `AttributeError`."""
    geom = Geom(
        name="box.geom",
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
    body = Body(
        name="box",
        pos=(0, 0, 0.4),
    )

    with pytest.raises(AttributeError):
        _ = body.geom

    # add child
    body.add_child(geom)
    assert id(geom) == id(body.geom)
