"""PET-Physics core."""

from __future__ import annotations

import mujoco
import numpy as np
import structlog

from pet_physics.constants import DEFAULT_SIM_END, DEFAULT_TELEPORT_INTERVAL
from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.callbacks.callback_orchestrator import CallbackOrchestrator

logger = structlog.get_logger(__name__)


class PETPhysicsCore:
    """Instances of this class are responsible to run a simulation in MuJoCo. In detail, it performs the single steps
    in the simulation and handle the body teleports.
    """

    def __init__(
        self,
        model: mujoco.MjModel,
        stability_check: "StabilityCheck",
        body_teleports: list | None = None,
        total_simulation_time: float | None = None,
        teleport_interval: float | None = None,
        callbacks: list[BaseCallback] | None = None,
    ) -> None:
        """Constructor of the mujoco simulation core.

        Args:
            model: The MuJoCo model that is simulated.
            stability_check: The required stability check. This influences the simulation.
            body_teleports: A list of body teleports that are applied during the simulation.
            total_simulation_time: The total simulation time in seconds.
            teleport_interval: The time that elapses between two teleports in seconds.
            callbacks: A list of callbacks that are called after each `step` of the core.
        """
        self._model = model
        """The MuJoCo model that is simulated."""
        self._data = mujoco.MjData(self._model)
        """The MuJoCo data that belongs to the model."""
        self._counter_mj_step_calls: int = 0
        """A counter that counts how often `mujoco.mj_step` has been called."""
        self._total_simulation_time = self._init_total_simulation_time(stability_check, total_simulation_time)
        """The total simulation time in seconds."""
        self._run_timestep: float = 1 / 5  # is set in `init_for_run`
        """The timestep of the simulation run. A bigger ratio, e.g., `1/30`, leads to a faster simulation than a 
        smaller ratio, e.g., `1/60`."""

        self._body_teleporter = None
        """The teleporter that is responsible for applying the body teleports at the correct time."""
        self._body_teleports: list = body_teleports or []
        """The list of body teleports that are applied in the simulation."""
        self._teleport_interval = teleport_interval or DEFAULT_TELEPORT_INTERVAL
        """The time that elapses between two teleports in seconds."""

        self._callback_orchestrator = CallbackOrchestrator(callbacks or [])
        """The orchestrator that handles all callbacks."""

    @property
    def model(self) -> mujoco.MjModel:
        """The MuJoCo model for the simulation."""
        return self._model

    @property
    def data(self) -> mujoco.MjData:
        """The MuJoCo data that belongs to the model."""
        return self._data

    @property
    def total_simulation_time(self) -> float:
        """The total simulation time in seconds."""
        return self._total_simulation_time

    @property
    def body_teleporter(self) -> None:
        """The teleporter that is responsible for applying the body teleports at the correct time."""
        return self._body_teleporter

    @property
    def teleport_interval(self) -> float:
        """The time that elapses between two teleports in seconds."""
        return self._teleport_interval

    @property
    def simulation_time(self) -> float:
        """The current simulation time."""
        return self._data.time

    @property
    def mj_model_timestep(self) -> float:
        """The timestep of the simulation as specified in the model."""
        return self._model.opt.timestep

    @property
    def run_timestep(self) -> float:
        """The timestep of the simulation run. A bigger ratio, e.g., `1/30`, leads to a faster simulation than a
        smaller ratio, e.g., `1/60`."""
        return self._run_timestep

    @property
    def n_mj_steps(self) -> int:
        """The number of `mujoco.mj_step` calls that have been executed since the last reset."""
        # Alternatively, one can compute the number of mj_step calls by:
        # > data.time / model.opt.timestep
        return self._counter_mj_step_calls

    @property
    def mj_steps_per_core_run_timestep(self) -> int:
        """Computes the number of `mujoco.mj_step` calls that are executed in one `PETPhysicsCore` run timestep."""
        return int(self.run_timestep / self.mj_model_timestep)

    @property
    def mj_step_index_final(self) -> int:
        """The index of the last `mujoco.mj_step` call in the simulation."""
        return int(self.total_simulation_time / self.mj_model_timestep)

    @staticmethod
    def _init_total_simulation_time(stability_check: "StabilityCheck", total_simulation_time: float | None) -> float:
        """Initializes the total simulation time.

        TODO(florian): Move this method in a core helpers module. Refactor it to make it clearer.

        Args:
            stability_check: The required stability check. This influences the simulation.
            total_simulation_time: The total simulation time in seconds.

        Returns:
            The total simulation time in seconds.
        """
        simulation_duration = total_simulation_time or DEFAULT_SIM_END
        # duration_in_config = stability_check.check_configuration.total_simulation_time_seconds

        # if stability_check.is_type_one_by_one:
        #     logger.warning("ignoring simulation duration from stability check configuration")
        #     return simulation_duration

        # elif stability_check.is_type_static:
        #     if duration_in_config is not None and (duration_in_config != simulation_duration):
        #         logger.info(
        #             f"use simulation duration from stability check configuration ({duration_in_config} seconds)"
        #         )
        #     # use simulation duration from configuration if defined
        #     return duration_in_config or simulation_duration

        return simulation_duration

    def run(self) -> None:
        """Runs the core as long as the simulation has finished."""
        try:
            sim_finished = False
            while not sim_finished:
                sim_finished = self.step()

        except Exception as e:
            logger.exception(e)

        logger.info("simulation stopped")
        self._callback_orchestrator.post_run()

    def _gracefully_place_boxes(self) -> None:
        """This method is called in the initialization of a run. It disables gravity, then runs a few, e.g., 100,
        simulation steps. After completing this "warm-up" phase, the gravity is gradually reset to its original value.
        """
        # Temporarily disable gravity
        original_gravity = np.copy(self._model.opt.gravity)
        self._model.opt.gravity[:] = 0

        # Place boxes and run simulation without gravity
        # This lets them settle into contact without falling
        for _ in range(100):
            mujoco.mj_step(self._model, self._data)

        # Re-enable gravity gradually
        for step in range(100):
            factor = step / 100
            self._model.opt.gravity = original_gravity * factor
            mujoco.mj_step(self._model, self._data)
        self._model.opt.gravity = original_gravity

        # Set the simulation time to zero
        self._data.time = 0

    def init_for_run(self, run_timestep: float) -> None:
        """Initializes everything before a run is started.

        Args:
            run_timestep: Defines the time step of the simulation run. A bigger ratio, e.g., `1/30`, leads to a
                faster simulation than a smaller ratio, e.g., `1/60`.
        """
        self._run_timestep = run_timestep

        self._reset_mj_data()

        self._gracefully_place_boxes()
        self.reinitialize_teleports()

        self._callback_orchestrator.initialize(self)

    def reinitialize_teleports(self) -> None:
        """Sets the body teleports back to the state it had at the start of the simulation."""
        pass

    def _do_mj_step(self) -> None:
        """Convenience method that executes a single MuJoCo simulation step by calling `mujoco.mj_step`."""
        mujoco.mj_step(self._model, self._data)
        self._counter_mj_step_calls += 1

    def _reset_mj_data(self) -> None:
        """Convenience method that resets the MuJoCo data to its initial state by calling `mujoco.mj_resetData`."""
        mujoco.mj_resetData(self._model, self._data)
        self._counter_mj_step_calls = 0

    def step(self) -> bool:
        """Executes MuJoCo simulation steps and applies a body teleport if the criterion for a teleport is met.

        Returns:
            Indicates whether the simulation has finished.
        """

        # Actual simulation step
        self._do_mj_step()
        callback_terminates_simulation = self._callback_orchestrator.call()

        # Apply teleport if required
        # if self._body_teleporter.is_time_for_teleport(self.simulation_time, self.teleport_interval):
        #     n_remaining_teleports = len(self._body_teleporter.body_teleports)
        #     end_in_print = "" if n_remaining_teleports > 1 else "\r"
        #     print(f"\rapply teleport / remaining teleports = {str(n_remaining_teleports).rjust(3)}", end=end_in_print)
        #     self._body_teleporter.apply_next_teleport(self._data, self.simulation_time)

        logger.debug(f"current step: {self.n_mj_steps} (sim_time = {round(self.simulation_time, 3)})")

        # Check whether simulation terminates after this step
        sim_finished = (
            (self.n_mj_steps >= self.mj_step_index_final)
            or (self.simulation_time >= self.total_simulation_time)
            or callback_terminates_simulation
        )

        return sim_finished

    def reset(self) -> None:
        """Resets the core to its initial state. This method is called, e.g., when a reset is triggered in the viewer
        callback."""
        self._reset_mj_data()
        self._callback_orchestrator.reset()

        self.reinitialize_teleports()
