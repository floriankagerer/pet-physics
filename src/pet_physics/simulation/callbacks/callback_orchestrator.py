"""This module contains a class that is responsible for orchestrating callbacks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from pet_physics.simulation.callbacks import CallbackWithMjSteps
from pet_physics.simulation.callbacks.call_schedule import CallSchedule
from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback

if TYPE_CHECKING:
    from pet_physics.simulation.callbacks.base_callback import BaseCallback
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore


CALLBACK_TYPE_SORTING_KEY_MAPPING = {
    ViewerCallback: 0,
}
"""The sorting key mapping for the callbacks. The lower the value, the earlier the callback is called. If the recorder
class is not present in the mapping, it is assigned the value `len(CALLBACK_TYPE_SORTING_KEY_MAPPING)`.

Reason for this sorting is to call *some* callbacks in the correct order. For example, the
`EarlyTerminationIfAnyBoxTouchesFloorCallback` works with the MjData object of MuJoCo, so it should be called **after**
the recorder callbacks, which write the data of the MjData object to the collection of body quantities. This is required
since the evaluator classes work with the quantity histories.
"""

logger = structlog.get_logger(__name__)


class CallbackOrchestrator:
    """Orchestrates callbacks by managing their registration and determining when to call each one."""

    def __init__(self, callbacks: list[BaseCallback]) -> None:
        """The constructor.

        Args:
            callbacks: The callbacks that are orchestrated.
        """
        self._callbacks = self._sort_callbacks(callbacks)
        """The callbacks that are orchestrated."""

        self._call_schedule: CallSchedule | None = None
        """A schedule that maps each simulation step to the callbacks that are called in this step."""

    @staticmethod
    def _sort_callbacks(callbacks: list[BaseCallback]) -> list[BaseCallback]:
        """Sorts the callbacks based on their type.

        Args:
            callbacks: The callbacks to be sorted.

        Returns:
            The sorted callbacks.
        """
        sorted_callbacks = sorted(
            callbacks,
            key=lambda callback: CALLBACK_TYPE_SORTING_KEY_MAPPING.get(
                type(callback), len(CALLBACK_TYPE_SORTING_KEY_MAPPING)
            ),
        )
        logger.debug(f"Sorted callbacks: {[type(callback).__name__ for callback in sorted_callbacks]}")

        return sorted_callbacks

    @property
    def _pet_physics_core(self) -> PETPhysicsCore:
        """The MuJoCo core of the first callback."""
        if not self._callbacks:
            msg = "The orchestrator does not contain any callbacks, so no MuJoCo core is available."
            raise RuntimeError(msg)

        return self._callbacks[0].core

    def initialize(self, core: PETPhysicsCore) -> None:
        """Initializes all registered callbacks.

        Args:
            core: The MuJoCo core that is passed to each callback.
        """
        callbacks_with_mj_step_indices: list[CallbackWithMjSteps] = []

        for callback in self._callbacks:
            relevant_mj_step_indices = callback.init_callback(core)

            if relevant_mj_step_indices is not None:
                callbacks_with_mj_step_indices.append((callback, relevant_mj_step_indices))

        self._call_schedule = CallSchedule.from_callbacks_with_mj_steps(callbacks_with_mj_step_indices)

    def call(self) -> bool:
        """Calls each callback.

        Returns:
            Indicates that any callback triggers the end of the simulation.
        """
        callback_terminates_simulation = False

        scheduled_callbacks = self._call_schedule.items.get(self._pet_physics_core.n_mj_steps, [])

        for callback in scheduled_callbacks:
            sim_end = callback.call()
            callback_terminates_simulation = callback_terminates_simulation or sim_end

        return callback_terminates_simulation

    def reset(self) -> None:
        """Resets all registered callbacks."""
        for callback in self._callbacks:
            callback.reset()

    def post_run(self) -> None:
        """Calls the `post_run` method of all registered callbacks."""
        for callback in self._callbacks:
            callback.post_run()
