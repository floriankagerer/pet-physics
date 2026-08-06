"""This module contains the base class for every recorder."""

from abc import ABC, abstractmethod

import mujoco

from pet_physics.simulation.physical_quantities.data_model.simulation_time import SimulationTime
from pet_physics.simulation.physical_quantities.history.base_history import BaseHistory
from pet_physics.wrapper.data_extractor import DataExtractor


class BaseRecorder(ABC):
    """The base class for any recorder.

    The main goal of a recorder is to extract a defined quantity in every simulation step and store the values of this
    quantity in each simulation step for every body in the MuJoCo simulation.
    """

    def __init__(self, mj_model: mujoco.MjModel, bodies: list[str], n_steps: int) -> None:
        """Initializes the recorder and sets attributes that all child classes need.

        Args:
            n_steps (int): The number of simulation steps.
            model (MjModel): The MuJoCo model.
            bodies (list[str]): The name of the bodies that are defined in the MuJoCo modelling XML file.
        """
        self._mj_model = mj_model
        """The MuJoCo model."""

        self._global = {"bodies": bodies, "sim_time": SimulationTime(n_steps)}
        """Quantities that are global, i.e., related to the simulation and model, respectively."""

    @property
    def bodies(self) -> list[str]:
        """The name of the bodies that are defined in the MuJoCo modelling XML file."""
        return self._global.get("bodies", [])

    @property
    def sim_time(self) -> SimulationTime:
        """The simulation time."""
        return self._global.get("sim_time")

    @abstractmethod
    def record(self, step_index: int, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        """Records some data in this simulation step.

        **Must be implemented by child class.**

        Args:
            step_index (int): The step index.
            model (MjModel): The MuJoCo model.
            data (MjData): The MuJoCo data object.
        """
        raise NotImplementedError("must be implemented by child class")

    def record_simulation_time(self, step_index: int, data: mujoco.MjData) -> None:
        """Records the simulation time in the current step.

        Args:
            step_index (int): The step index.
            data (MjData): The MuJoCo data object.
        """
        self.sim_time.set_ith_value(step_index, DataExtractor.simulation_time(data))

    @abstractmethod
    def get_quantity_history_registrations(self) -> list[tuple[str, BaseHistory]]:
        """Returns a list of tuples where each tuple contains the quantity name and its corresponding history object.

        This method is used to register the histories in the `CollectionBodyQuantities`.

        Returns:
            list[tuple[str, BaseHistory]]: A list of tuples where each tuple contains the quantity name and its
                corresponding history object.
        """
        raise NotImplementedError("must be implemented by child class")
