"""Data model for the MJCF `exclude` contact element.

Defines the `Exclude` dataclass, which mirrors the attributes of the `<exclude>` element in the MJCF XML schema and
can be serialized back to XML via `BaseMJCFObject.to_xml_string()`.
"""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass
class Exclude(BaseMJCFObject):
    """Represents the exclude element in the contact section of a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#contact-exclude

    Attributes:
        body1: The name of the first body in the pair that is excluded from collision checking.
        body2: The name of the second body in the pair that is excluded from collision checking.
        name: An optional name of this exclude pair.
    """

    body1: str
    body2: str
    name: str | None = None
