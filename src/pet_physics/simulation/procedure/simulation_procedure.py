"""This module contains multiple simulation procedure classes."""

from abc import ABC
from dataclasses import dataclass
from typing import Literal

from pet_physics.modeling.model_generation.model_generator_configuration import (
    ModelGeneratorConfiguration,
    RigidCG,
    RigidNewton,
    SoftNewton,
)


@dataclass
class SimulationProcedure(ABC):
    """The base class of any simulation procedure.

    Attributes:
        name: The name of the simulation procedure.
        model_generator_configurations: The configurations of the model generator for this procedure.
    """

    name: str
    model_generator_configurations: list[ModelGeneratorConfiguration]


@dataclass
class DefaultSimulationProcedure(SimulationProcedure):
    """The default simulation procedure. It contains three model generator configurations."""

    def __init__(self) -> None:
        super().__init__(
            name="default",
            model_generator_configurations=[RigidNewton(), RigidCG(), SoftNewton()],
        )


@dataclass
class RigidSimulationProcedure(SimulationProcedure):
    """The default simulation procedure. It contains two model generator configurations."""

    def __init__(self) -> None:
        super().__init__(
            name="rigid",
            model_generator_configurations=[RigidNewton(), RigidCG()],
        )


SimulationProcedureNames = Literal["default", "rigid"]
"""Type alias for the literals that are valid simulation procedure names."""

SIMULATION_PROCEDURE_MAPPER = {
    "default": DefaultSimulationProcedure(),
    "rigid": RigidSimulationProcedure(),
}
"""Maps the name of a simulation procedure to its object."""
