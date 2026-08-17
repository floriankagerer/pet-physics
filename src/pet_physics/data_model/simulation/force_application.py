"""Classes defining force applications for the MuJoCo simulation."""

from dataclasses import dataclass
from typing import Self

from pet_physics.type_alias_definition import Vector3d


@dataclass
class RelativeForceApplication:
    """A force vector expressed as percentages of a reference force magnitude.

    Attributes:
        start_time: Simulation time in seconds at which the force application starts.
        duration: Duration in simulation seconds for which the force application is active.
        percentage_vector: Relative force vector as percentages in x-, y-, and z-direction.
    """

    start_time: float
    duration: float
    percentage_vector: Vector3d

    @property
    def end_time(self) -> float:
        """The end time of the force application."""
        return self.start_time + self.duration


@dataclass
class AbsoluteForceApplication:
    """A force vector in Newton applied to a named body at a given simulation time.

    Attributes:
        start_time: Simulation time in seconds at which the force application starts.
        duration: Duration in simulation seconds for which the force application is active.
        force_vector: Absolute force vector in Newton in x-, y-, and z-direction.
        target: Name of the body to which the force is applied.
    """

    start_time: float
    duration: float
    force_vector: Vector3d
    target: str

    @property
    def end_time(self) -> float:
        """The end time of the force application."""
        return self.start_time + self.duration

    @classmethod
    def from_relative_force_application(
        cls, relative_force_application: RelativeForceApplication, magnitude: float, target: str
    ) -> Self:
        """Scale a `RelativeForceApplication` by a magnitude to produce absolute Newton values.

        Args:
            relative_force_application: The relative force application to convert.
            magnitude: The scalar used to scale the percentage force vector.
            target: Name of the body to which the force is applied.

        Returns:
            The corresponding `AbsoluteForceApplication` with a scaled force vector.
        """

        force_vector = [component * magnitude for component in relative_force_application.percentage_vector]

        return cls(
            start_time=relative_force_application.start_time,
            duration=relative_force_application.duration,
            force_vector=force_vector,
            target=target,
        )
