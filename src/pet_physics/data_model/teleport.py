"""Data model for the teleportation of bodies in a MuJoCo simulation."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from pet_physics.type_alias_definition import Position3d


@dataclass_json
@dataclass
class Teleport:
    """Represents the target position of a body with the given name.

    Attributes:
        name: The name of a body as it is specified in the MuJoCo modelling file
        target_position: The target position of this body, i.e., the coordinates the body is placed at after teleporting.
        initial_position: The initial position of this body, i.e., the coordinates the body is placed at
            before teleporting.
    """

    name: str
    target_position: Position3d
    initial_position: Position3d

    @property
    def delta_position(self) -> Position3d:
        """The delta position, i.e., the target position minus the initial position."""
        delta = [self.target_position[idx] - self.initial_position[idx] for idx in range(len(self.target_position))]
        return tuple(delta)
