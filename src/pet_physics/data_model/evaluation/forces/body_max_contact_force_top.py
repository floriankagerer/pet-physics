"""Data model for storing maximum top contact force values per body."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BodyMaxContactForceTop:
    """Stores the maximum contact force acting on top of a single body.

    Attributes:
        name: The name of the body.
        max_contact_force_top: The maximum value of the contact forces that act on top of this body.
    """

    name: str
    max_contact_force_top: float
