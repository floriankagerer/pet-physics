"""Threshold configuration for evaluating acceptable pose deltas in a simulation."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ThresholdPoseDelta:
    """Thresholds for deciding whether a body's pose deviation is within acceptable limits.

    Attributes:
        max_x_delta_m: Maximum allowed deviation in the x-position (in meters) such that a packing plan still counts
            as stable.
        max_y_delta_m: Maximum allowed deviation in the y-position (in meters) such that a packing plan still counts
            as stable.
        max_z_delta_m: Maximum allowed deviation in the z-position (in meters) such that a packing plan still counts
            as stable.
        max_tiltedness_degrees: Maximum allowed tilt of the body (in degrees) such that a packing plan still counts
            as stable.
    """

    max_x_delta_m: float = 0.02
    max_y_delta_m: float = 0.02
    max_z_delta_m: float = 0.02
    max_tiltedness_degrees: float = 20.0
