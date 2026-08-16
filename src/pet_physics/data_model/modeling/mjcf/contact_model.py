from dataclasses import dataclass
from xml.etree.ElementTree import Element

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass
class ContactModel(BaseMJCFObject):
    """Represents the contact section in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact
    """

    def to_xml(self) -> Element:
        return super().to_xml(tag="contact")
