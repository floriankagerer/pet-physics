"""This module tests the data model of a `Flexcomp` object."""

from pet_physics.data_model.modeling.mjcf.contact import Contact
from pet_physics.data_model.modeling.mjcf.edge import Edge
from pet_physics.data_model.modeling.mjcf.flexcomp import Flexcomp


def test_flexcomp_to_xml_string():
    """Tests the constructor of the `Flexcomp` dataclass."""
    # without children
    flexcomp_obj = Flexcomp(
        name="test_flexcomp",
        pos=(0.3, 0.2, 0.1),
        mass=3.14,
        spacing=(0.1, 0.1, 0.1),
        dim=3,
        type="box",
        rigid="false",
        count=(10, 10, 10),
        rgba=(1, 0, 0, 1),
        radius=0.1,
    )
    expected_xml_string = """<flexcomp name="test_flexcomp" pos="0.3 0.2 0.1" mass="3.14" count="10 10 10" spacing="0.1 0.1 0.1" dim="3" type="box" rigid="false" rgba="1 0 0 1" radius="0.1" />"""

    assert flexcomp_obj.to_xml_string() == expected_xml_string

    # with multiple children
    edge_obj = Edge(equality="true")
    flexcomp_obj.add_child(edge_obj)

    expected_xml_string = """<flexcomp name="test_flexcomp" pos="0.3 0.2 0.1" mass="3.14" count="10 10 10" spacing="0.1 0.1 0.1" dim="3" type="box" rigid="false" rgba="1 0 0 1" radius="0.1"><edge equality="true" /></flexcomp>"""
    assert flexcomp_obj.to_xml_string() == expected_xml_string

    contact_obj = Contact(
        internal="false",
        selfcollide="none",
        solref=(0.1, 0.2),
        solimp=(0.99, 0.99, 0.01),
        friction=(0.5, 0.005, 0.0001),
    )
    flexcomp_obj.add_child(contact_obj)
    expected_contact_xml_string = """<contact internal="false" selfcollide="none" solref="0.1 0.2" solimp="0.99 0.99 0.01" friction="0.5 0.005 0.0001" />"""

    expected_xml_string = f"""<flexcomp name="test_flexcomp" pos="0.3 0.2 0.1" mass="3.14" count="10 10 10" spacing="0.1 0.1 0.1" dim="3" type="box" rigid="false" rgba="1 0 0 1" radius="0.1"><edge equality="true" />{expected_contact_xml_string}</flexcomp>"""
    assert flexcomp_obj.to_xml_string() == expected_xml_string
