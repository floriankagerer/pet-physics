"""This module contains the `BaseHistory` class, which serves as the base class for tracking physical quantities
during a MuJoCo simulation."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any

import mujoco

from pet_physics.simulation.mujoco_lookup_helpers import get_body_names_in_model, get_geom_names_of_body


class BaseHistory(ABC):
    """The base class for any storing of physical quantities during the simulation."""

    def __init__(self, mj_model: mujoco.MjModel, n_steps: int) -> None:
        self._mj_model = mj_model
        """The MuJoCo model."""

        self._n_steps = n_steps
        """The number of steps to be tracked."""

        self._bodies = get_body_names_in_model(model=mj_model)
        """The name of the bodies in the MuJoCo modelling XML file."""

        self._body_name_to_geom_names = {
            body_name: get_geom_names_of_body(self._mj_model, body_name=body_name) for body_name in self._bodies
        }
        """A dictionary that maps body names to their corresponding geometry names."""

        self._values = self._init_values()
        """A dictionary that contains the body name as key and a list of tracked values as values."""

    def body_name_with_values(self) -> Generator[str, list[Any], None]:
        """Generator that yields body names along with their corresponding tracked values.

        Yields:
            A generator yielding tuples of body names and their tracked values.
        """
        for body_name in self._bodies:
            yield body_name, self.get_values_of_body(body_name)

    @abstractmethod
    def _init_values(self) -> dict[str, list[Any]]:
        """Initializes the dictionary that contains the tracked values for each body."""
        # For example: {body_name: [None] * self._n_steps for body_name in self._bodies}
        raise NotImplementedError("This method must be implemented by subclasses.")

    @abstractmethod
    def _set_specific_value(self, body_name: str, step_index: int, value: Any) -> None:
        """Sets the specific tracked value for a body in a specific simulation step."""
        # For example: self._values[body_name][step_index] = value
        raise NotImplementedError("This method must be implemented by subclasses.")

    def track_value_of_body_in_step(self, body_name: str, step_index: int, value: Any) -> None:
        """Tracks the value of a specific body in a specific simulation step.

        Args:
            body_name: The name of the body.
            step_index: The step index.
            value: The value to be tracked.
        """
        self._set_specific_value(body_name=body_name, step_index=step_index, value=value)

    def get_values_of_body(self, body_name: str) -> list[Any]:
        """Returns the tracked values of a specific body.

        Args:
            body_name: The name of the body.

        Returns:
            The list of tracked values for the specified body.
        """
        return self._values[body_name]
