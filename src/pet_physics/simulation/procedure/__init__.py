"""This module contains objects that are used to control the MuJoCo simulation."""

from pet_physics.simulation.procedure.simulation_procedure import (
    SIMULATION_PROCEDURE_MAPPER,
    SimulationProcedure,
    SimulationProcedureNames,
)


def get_simulation_procedure(name: SimulationProcedureNames) -> SimulationProcedure:
    """Returns the simulation procedure, requested by its name.

    Args:
        name: The name of the requested simulation procedure.

    Returns:
        The requested simulation procedure.

    Raises:
        ValueError: If the requested simulation procedure is not defined.
    """
    if name not in SIMULATION_PROCEDURE_MAPPER:
        raise ValueError(f"simulation procedure '{name}' is not defined")

    return SIMULATION_PROCEDURE_MAPPER[name]
