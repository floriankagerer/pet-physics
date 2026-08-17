"""Data model for the configuration of bodies in a MuJoCo simulation."""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.teleport import Teleport


@dataclass
class BodiesConfiguration:
    """Description of the bodies, their source and target positions.

    Attributes:
        bodies: The list of bodies that are placed in the simulation.
        teleports: The list of teleports that define the source and target positions for each body.
    """

    bodies: list[Body]
    teleports: list[Teleport]
