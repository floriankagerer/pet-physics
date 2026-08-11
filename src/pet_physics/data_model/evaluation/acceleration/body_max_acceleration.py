"""Data model for storing maximum acceleration values per body."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BodyMaxAcceleration:
    """Stores the maximum linear and angular acceleration values for a single body.

    Attributes:
        name: The name of the body.
        max_linear_acceleration: The maximum value of the linear acceleration.
        max_angular_acceleration: The maximum value of the angular acceleration.
    """

    name: str
    max_linear_acceleration: float
    max_angular_acceleration: float
