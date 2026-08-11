"""This module contains callbacks that can be used to terminate the simulation early."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import structlog

from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.drop_detection.box_fall_off_carrier_detector import BoxFallOffCarrierDetector
from pet_physics.type_alias_definition import Size3d
from pet_physics.utils.quaternion_utils import oriented_size

if TYPE_CHECKING:
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore

logger = structlog.get_logger(__name__)


class EarlyTerminationIfAnyBoxTouchesFloorCallback(BaseCallback):
    """Terminates the simulation if any box falls off the pallet or touches the floor.

    It is independent of other callbacks since it works with the data object of MuJoCo.
    """

    def __init__(
        self,
        body_name_to_size_mapping: dict[str, Size3d] | None = None,
        call_every_nth_mj_step: int | None = None,
        distance_below_top_side_of_carrier_to_consider_as_not_touching_floor: float | None = None,
    ) -> None:
        """Constructor of this class.

        Args:
            body_name_to_size_mapping: The dimensions of the boxes in the simulation. The keys of the dict are
                the names of the boxes as they are specified in the MJCF, and the values are the dimensions of
                the boxes.
            call_every_nth_mj_step: Identifies whether this callback should be called every n-th `mujoco.mj_step` call.
                If `None`, the time step of the `PETPhysicsCore` is used, i.e., the callback is called every
                `core.run_timestep / core.mj_model_timestep`.
            distance_below_top_side_of_carrier_to_consider_as_not_touching_floor: This value defines the distance below
                the top side of the carrier such that a body is not considered as touching the floor. If `None`, a
                default value is used (`0.1`, meaning, 0.1 meters).
        """
        super().__init__()

        self._body_name_to_size_mapping: dict[str, Size3d] | None = body_name_to_size_mapping
        """Contains the body names and keys and their sizes are the corresponding values."""

        self._call_every_nth_mj_step = call_every_nth_mj_step
        """Identifies whether this callback should be called every n-th `mujoco.mj_step` call. If `None`, the time step
        of the `PETPhysicsCore` is used, i.e., the callback is called every `core.run_timestep / core.mj_model_timestep`."""

        self._box_fall_off_carrier_detector = BoxFallOffCarrierDetector(
            distance_below_top_side_of_carrier_to_consider_as_not_touching_floor=distance_below_top_side_of_carrier_to_consider_as_not_touching_floor,
        )
        """Detects whether a box has fallen off the pallet during the simulation."""

    @property
    def body_name_to_size_mapping(self) -> dict[str, Size3d]:
        """The body name to size mapping."""
        if self._body_name_to_size_mapping is None:
            raise RuntimeError("The body name to size mapping is not set. Please set it before using this method.")

        return self._body_name_to_size_mapping

    @body_name_to_size_mapping.setter
    def body_name_to_size_mapping(self, value: dict[str, Size3d]) -> None:
        self._body_name_to_size_mapping = value

    def init_callback(self, core: PETPhysicsCore) -> list[int]:
        """Initializes the callback, e.g., by setting the simulation core and preparing any necessary data.

        In general, this method is called **before** the first `core.step` call.

        Args:
            core: The core this callback is added to.

        Returns:
            The list of `mujoco.mj_step` call indices at that this callback is called.
        """
        self._core = core

        self.reset()

        relevant_mj_step_indices = self.call_on_every_nth_mj_step(self._call_every_nth_mj_step)

        return relevant_mj_step_indices

    def _get_position_and_quaternion_of_body(self, body_name: str) -> tuple[np.ndarray, np.ndarray]:
        """Returns the position and quaternion of the body with the given name as specified in the MuJoCo data object.

        Args:
            body_name: The name of the body to get the position and quaternion for.

        Returns:
            The position and quaternion of the body with the given name as they are specified in the data object of
                MuJoCo.
        """
        body_id = self.get_body_id(body_name)

        position_from_mj_data = self._core.data.xpos[body_id]
        quaternion_from_mj_data = self._core.data.xquat[body_id]

        return position_from_mj_data, quaternion_from_mj_data

    def call(self) -> bool:
        """Checks whether the simulation should be terminated, e.g., because a box touched the floor.

        Returns:
            `True` if the simulation should terminate, `False` otherwise.
        """

        for body_name, body_size in self.body_name_to_size_mapping.items():
            body_center_of_mass, body_quaternion = self._get_position_and_quaternion_of_body(body_name)
            body_oriented_size = oriented_size(size=body_size, quat=body_quaternion)

            if self._box_fall_off_carrier_detector.detect(
                position_center_of_mass=body_center_of_mass, oriented_size=body_oriented_size
            ):
                logger.warning(f"Early termination triggered due to body '{body_name}' touching the floor.")
                return True

        return False

    def post_run(self) -> None:
        """This method is called **after** a `core.run` has completed."""
        # nothing to do after run
        pass

    def reset(self) -> None:
        """This method resets the object such that it is in its initial state."""
        pass
