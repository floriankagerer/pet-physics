from pet_physics.data_model.modeling.mjcf.contact_model import ContactModel
from pet_physics.data_model.modeling.mjcf.exclude import Exclude


def test_contact_model_to_xml_string():
    contact = ContactModel()

    assert contact.to_xml_string() == "<contact />"

    exclude1 = Exclude("_body0", "body1")
    exclude2 = Exclude("_body0", "body2")

    exclude1_xml_string = """<exclude body1="_body0" body2="body1" />"""
    exclude2_xml_string = """<exclude body1="_body0" body2="body2" />"""

    contact.add_child(exclude1).add_child(exclude2)

    expected_xml_string = f"""<contact>{exclude1_xml_string}{exclude2_xml_string}</contact>"""

    assert contact.to_xml_string() == expected_xml_string
