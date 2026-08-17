"""Data model for force application profiles in MuJoCo simulations."""

from typing import Self

import structlog

from pet_physics.data_model.model_configuration import ModelConfiguration
from pet_physics.data_model.simulation.force_application import AbsoluteForceApplication

logger = structlog.get_logger(__name__)


class ForceApplicationProfile:
    """An ordered sequence of `AbsoluteForceApplication` instances applied during a simulation."""

    def __init__(self, forces: list[AbsoluteForceApplication] | None = None) -> None:
        """Populate the profile from an optional list of force applications.

        Args:
            forces: Initial force applications; defaults to an empty list when not provided.
        """
        self._forces = forces or []

    def __add__(self, other: Self) -> Self:
        """Combine the forces of two profiles into a new `ForceApplicationProfile`.

        Args:
            other: The other profile whose forces are appended.

        Returns:
            A new profile containing the forces from both profiles.
        """
        if not isinstance(other, ForceApplicationProfile):
            return NotImplemented
        return ForceApplicationProfile(self._forces + other._forces)

    def __iadd__(self, other: Self) -> Self:
        """Extend this profile in-place with the forces from another profile.

        Args:
            other: The profile whose forces are appended to this one.

        Returns:
            This profile after extension.
        """
        if not isinstance(other, ForceApplicationProfile):
            return NotImplemented
        self._forces.extend(other._forces)
        return self

    @property
    def forces(self) -> list[AbsoluteForceApplication]:
        """The list of forces to be applied in this profile."""
        return self._forces

    @property
    def number_forces(self) -> int:
        """The number of force applications in this profile."""
        return len(self._forces)

    @property
    def application_time_range(self) -> tuple[float, float]:
        """The time range (start_time, end_time) covered by the force applications."""
        start_time = min(self._forces, key=lambda force: force.start_time).start_time
        end_time = max(self._forces, key=lambda force: force.start_time).start_time

        return (start_time, end_time)

    def set_force_targets(
        self, sorted_target_names: list[str], target_validation: ModelConfiguration | None = None
    ) -> None:
        """Assign a target body to each force in the profile.

        Body names must be provided in the same order as the forces in this profile. When
        `target_validation` is supplied, each target is verified to be a freejoint body so
        that the force application affects the simulation.

        Args:
            sorted_target_names: Body names to assign, one per force, in profile order.
                The length must equal the number of forces in this profile.
            target_validation: If provided, validates that each target is a freejoint body.
        """
        if len(sorted_target_names) != self.number_forces:
            msg = (
                f"The length of the given force targets list ({len(sorted_target_names)}) must be equal to the number "
                f"of forces in this profile ({self.number_forces})."
            )
            logger.error(msg)
            raise ValueError(msg)

        # Set target names
        for force, target_name in zip(self._forces, sorted_target_names):
            force.target = target_name

        # Validate targets
        if target_validation is None:
            logger.info("we do not validate whether the targets are modeled as bodies with a freejoint")
        else:
            self._validate_force_targets_are_freejoint_bodies(target_validation)

    def _validate_force_targets_are_freejoint_bodies(self, model_configuration: ModelConfiguration) -> None:
        """Raise `ValueError` if any force target body is not a freejoint body.

        Args:
            model_configuration: The model configuration used to look up body properties.
        """
        validated_target_names = set()

        bodies_in_model_configuration = [model_configuration.carrier] + model_configuration.boxes
        mapping_body_name_to_body = {body.name: body for body in bodies_in_model_configuration}

        for force in self._forces:
            force_target_name = force.target
            if force_target_name in validated_target_names:
                continue

            body = mapping_body_name_to_body[force_target_name]

            if not body.has_freejoint:
                msg = f"The body '{force_target_name}' to that a force is must be a freejoint body."
                logger.error(msg)
                raise ValueError(msg)

            validated_target_names.add(force_target_name)
