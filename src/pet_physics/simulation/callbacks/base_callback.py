"""The base class for every callback that is related to a simulation with MuJoCo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pet_physics.simulation.mujoco_lookup_helpers import get_body_id

if TYPE_CHECKING:
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore

_ABSTRACT_METHOD_ERROR_MSG = "Must be implemented by child class"


class BaseCallback(ABC):
    """The base class for any callback."""

    def __init__(self) -> None:
        self._core: PETPhysicsCore | None = None
        """The MuJoCo simulation core, which is initialized in `self.init_callback` later."""

    @property
    def core(self) -> PETPhysicsCore:
        """The MuJoCo simulation core."""
        if self._core is None:
            msg = (
                "The MuJoCo core has not been initialized in callback yet. "
                f"Please call '{self.init_callback.__name__}' first."
            )
            raise RuntimeError(msg)

        return self._core

    def get_body_id(self, body_name: str) -> int:
        """Gets the body id for a given body name.

        Args:
            body_name: The name of the body.

        Returns:
            The id of the body in the MuJoCo model.
        """
        body_id = get_body_id(model=self.core.model, body_name=body_name)
        return body_id

    def convert_simulation_time_to_mj_step_index(self, simulation_time: float) -> int:
        """Converts a simulation time to the corresponding ``mujoco.mj_step`` call index.

        To calculate the index, the time step that is defined in the mujoco model (MjModel) is used.

        Args:
            simulation_time: The simulation time to convert.

        Returns:
            The corresponding `mujoco.mj_step` call index.
        """
        return int(simulation_time / self.core.mj_model_timestep)

    def convert_simulation_times_to_mj_step_indices(self, simulation_times: list[float]) -> list[int]:
        """Converts a list of simulation times to the corresponding ``mujoco.mj_step`` call indices.

        Args:
            simulation_times: The simulation times to convert.

        Returns:
            The corresponding `mujoco.mj_step` call indices.
        """
        mj_step_indices = [self.convert_simulation_time_to_mj_step_index(sim_time) for sim_time in simulation_times]
        return mj_step_indices

    def call_on_every_nth_mj_step(self, n: int | None = None) -> list[int]:
        """Returns a list of indices that represent after which calls of ``mujoco.mj_step`` this callback is called.

        If no ``n`` is given, the time step of the ``PETPhysicsCore`` is used, i.e., the callback is called every
        ``core.run_timestep / core.mj_model_timestep``.

        Args:
            n: If given, the callback is called every n-th `mujoco.mj_step` call. If `None`, the time step of the
                `PETPhysicsCore` is used, i.e., the callback is called every `core.run_timestep / core.mj_model_timestep`.

        Returns:
            The list of `mujoco.mj_step` call indices at that this callback is called.
        """
        if n is None:
            call_on_every = self.core.mj_steps_per_core_run_timestep
        else:
            call_on_every = n

        # Determine last mj_step index
        last_mj_step_index = self.core.mj_step_index_final

        # Generate list of relevant mj_step indices
        relevant_mj_step_indices = list(range(0, last_mj_step_index + call_on_every - 1, call_on_every))
        return relevant_mj_step_indices

    @abstractmethod
    def init_callback(self, core: PETPhysicsCore) -> list[int]:
        """Initializes the callback, e.g., by setting the simulation core and preparing any necessary data.

        In general, this method is called **before** the first `core.step` call.

        Args:
            core: The core this callback is added to.

        Returns:
            The list of `mujoco.mj_step` call indices at that this callback is called.
        """
        raise NotImplementedError(_ABSTRACT_METHOD_ERROR_MSG)

    @abstractmethod
    def call(self) -> bool:
        """This method is called after each `core.step`. The return value indicates whether the simulation finishes."""
        raise NotImplementedError(_ABSTRACT_METHOD_ERROR_MSG)

    @abstractmethod
    def post_run(self) -> None:
        """This method is called **after** a `core.run` has completed."""
        raise NotImplementedError(_ABSTRACT_METHOD_ERROR_MSG)

    @abstractmethod
    def reset(self) -> None:
        """This method resets the object such that it is in its initial state."""
        raise NotImplementedError(_ABSTRACT_METHOD_ERROR_MSG)
