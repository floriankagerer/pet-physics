"""Data model for storing the pose delta of a body relative to its planned position."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from pet_physics.type_alias_definition import Vector3d


@dataclass_json
@dataclass
class BodyPoseDelta:
    """Stores the name, position delta, and maximum tiltedness for a single body.

    Attributes:
        name: The name of the body.
        final_position_delta: The delta of the x-, y-, and z-coordinates from the body's final position in simulation
            and the expected position according to teleport.
        max_body_tiltedness: The maximal value of the angle that the unit normal in z-direction of this body has with
            the z-axis.
    """

    name: str
    final_position_delta: Vector3d
    max_body_tiltedness: float
