"""Defines a call schedule that maps simulation steps to their callbacks."""

from dataclasses import dataclass
from typing import Self

from pet_physics.simulation.callbacks import CallbackWithMjSteps
from pet_physics.simulation.callbacks.base_callback import BaseCallback


@dataclass
class CallSchedule:
    """A schedule mapping simulation steps to their respective callbacks.

    Attributes:
        items: A dict mapping each simulation step to the list of callbacks called at that step.
    """

    items: dict[int, list[BaseCallback]]

    @classmethod
    def from_callbacks_with_mj_steps(cls, callbacks_with_mj_steps: list[CallbackWithMjSteps]) -> Self:
        """Builds a call schedule indexed by simulation step from a list of callback-step pairs.

        Args:
            callbacks_with_mj_steps: A list of tuples, each containing a callback and its relevant simulation
                steps, e.g., `[(callback1, [0, 10, 20]), (callback2, [5, 15])]`.

        Returns:
            A `CallSchedule` with all callbacks mapped to their respective simulation steps.
        """
        call_schedule_items: dict[int, list[BaseCallback]] = {}

        for callback, relevant_mj_step_values in callbacks_with_mj_steps:
            for mj_step in relevant_mj_step_values:
                if mj_step not in call_schedule_items:
                    # Initialize the list if the step is not already in the schedule
                    call_schedule_items[mj_step] = []

                # Append the callback to the list for this step
                call_schedule_items[mj_step].append(callback)

        return cls(items=call_schedule_items)
