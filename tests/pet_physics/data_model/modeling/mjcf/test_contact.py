"""This module tests the data model of a `Contact` object."""

from pet_physics.data_model.modeling.mjcf.contact import Contact


def test_contact_to_xml_string():
    """Tests the constructor of the dataclass `Contact`."""
    contact = Contact(
        internal="false",
        selfcollide="none",
        solref=(0.1, 0.2),
        solimp=(0.99, 0.99, 0.01),
        friction=(0.5, 0.005, 0.0001),
    )
    expected_xml_string = """<contact internal="false" selfcollide="none" solref="0.1 0.2" solimp="0.99 0.99 0.01" friction="0.5 0.005 0.0001" />"""

    assert contact.to_xml_string() == expected_xml_string
