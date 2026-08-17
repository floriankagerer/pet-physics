"""A callback that applies forces to bodies in the MuJoCo simulation according to a given force application profile."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from pet_physics.data_model.simulation.force_application import AbsoluteForceApplication
from pet_physics.data_model.simulation.force_application_profile import ForceApplicationProfile
from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.type_alias_definition import Vector3d

if TYPE_CHECKING:
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore

logger = structlog.get_logger(__name__)


class ForceApplicatorCallback(BaseCallback):
    """A callback that applies forces to bodies in the MuJoCo simulation according to a given force application
    profile."""

    def __init__(self, force_application_profile: ForceApplicationProfile) -> None:
        super().__init__()

        self._force_application_profile = force_application_profile
        """The force application profile that defines which forces to apply at which time steps."""

        self._sorted_forces = self._get_forces_sorted_wrt_application_time(self._force_application_profile)
        """The list of forces to be applied, sorted with respect to their application time."""

        self._active_forces_body_ids: set[int] = set()
        """The set of body ids that currently have active forces applied to them."""

    def init_callback(self, core: PETPhysicsCore) -> list[int]:
        """Initializes the callback, e.g., by setting the simulation core and preparing any necessary data.

        In general, this method is called **before** the first `core.step` call.

        Args:
            core: The core this callback is added to.

        Returns:
            The list of `mujoco.mj_step` call indices at that this callback is called.
        """
        self._core = core

        force_application_start_times = [force.start_time for force in self._sorted_forces]
        relevant_mj_step_indices = self.convert_simulation_times_to_mj_step_indices(force_application_start_times)

        force_application_end_times = [force.end_time for force in self._sorted_forces]
        deactivation_mj_step_indices = self.convert_simulation_times_to_mj_step_indices(force_application_end_times)
        relevant_mj_step_indices.extend(deactivation_mj_step_indices)

        relevant_mj_step_indices.sort()

        return relevant_mj_step_indices

    def call(self) -> bool:
        """Called after each ``core.step``; checks whether it is time to apply the next force in the profile.

        Returns:
            `True` if the simulation should terminate, `False` otherwise.
        """
        self._reset_active_forces()
        if self._is_next_force_applicable():
            next_force_application = self._sorted_forces.pop(0)
            self._apply_force(next_force_application)

        return False

    def post_run(self) -> None:
        """This method is called **after** a `core.run` has completed."""
        # nothing to do after run
        pass

    def reset(self) -> None:
        """This method resets the object such that it is in its initial state."""

        self._sorted_forces = self._get_forces_sorted_wrt_application_time(self._force_application_profile)

    @staticmethod
    def _get_forces_sorted_wrt_application_time(
        force_application_profile: ForceApplicationProfile,
    ) -> list[AbsoluteForceApplication]:
        """Sorts the forces of the given profile with respect to their application time in ascending order.

        Args:
            force_application_profile: The force application profile containing the forces.

        Returns:
            A list of `AbsoluteForceApplication` instances sorted by the application time in *ascending order*, i.e.,
                the earliest application time first.
        """
        sorted_forces = sorted(force_application_profile.forces, key=lambda x: x.start_time)
        return sorted_forces

    def _is_next_force_applicable(self) -> bool:
        """Determines whether the next force is applicable at the current simulation time.

        Returns:
            `True` if the next force is applicable, `False` otherwise.
        """
        if not self._sorted_forces:
            # early exit if no forces are left to apply
            return False

        next_force = self._sorted_forces[0]

        application_time_mj_step = self.convert_simulation_time_to_mj_step_index(next_force.start_time)
        is_it_time = self.core.simulation_time >= next_force.start_time

        return (self.core.n_mj_steps == application_time_mj_step) or is_it_time

    def _apply_force(self, force_application: AbsoluteForceApplication) -> None:
        """Applies the given force in the simulation by setting the force in the MuJoCo data.

        Args:
            force_application: The force to be applied.
        """
        logger.info(
            (
                f"Applying force at step {self.core.n_mj_steps} /  at time {round(self.core.simulation_time, 3)}: "
                f"{force_application.force_vector}"
            )
        )

        body_id = self.get_body_id(force_application.target)

        self._set_force_in_mujoco_data(body_id, force_application.force_vector)
        self._active_forces_body_ids.add(body_id)

    def _set_force_in_mujoco_data(self, body_id: int, force_vector: Vector3d) -> None:
        """Sets the given force vector in the MuJoCo data for the given body id.

        Args:
            body_id: The body id to that the force is applied.
            force_vector: The force vector to apply.
        """
        self.core.data.xfrc_applied[body_id] = [*force_vector, 0, 0, 0]

    def _reset_active_forces(self) -> None:
        """Resets all active forces in the MuJoCo data to zero."""
        # TODO(florian): Refactor logic to only deactivate these forces on bodies, that are really supposed to be
        #   deactivated.
        for body_id in self._active_forces_body_ids:
            self._set_force_in_mujoco_data(body_id, (0, 0, 0))
            logger.info(f"Resetting force at step {self.core.n_mj_steps} on body id {body_id}.")

        self._active_forces_body_ids.clear()
