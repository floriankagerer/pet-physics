"""Provides force application profiles for simulations."""

from pet_physics.data_model.simulation.force_application import AbsoluteForceApplication
from pet_physics.data_model.simulation.force_application_profile import ForceApplicationProfile
from pet_physics.simulation.force_application.dummy_relative_force_applications import (
    get_dummy_relative_force_applications,
)
from pet_physics.simulation.force_application.radial_relative_force_applications import (
    get_radial_relative_force_applications,
)
from pet_physics.simulation.force_application.sin_dummy_relative_force_applications import (
    get_sin_dummy_relative_force_applications,
)


class ForceApplicationProfileProvider:
    """
    Provides force application profiles for simulations.

    The profile is received as a `ForceApplicationProfile` instance. You can define a reference magnitude for the
    forces and a time offset that is applied to all application times. Consequently, you can build different profiles
    by scaling the relative force vectors with the given magnitude and shifting the application times by the given
    offset.
    """

    @staticmethod
    def get_dummy_profile(
        magnitude: float, target: str, application_time_offset: float = 0.0
    ) -> ForceApplicationProfile:
        """
        Returns a dummy force application profile.

        Args:
            magnitude: The reference force magnitude in Newton.
            target: The name of the body to that the forces of this profile are applied.
            application_time_offset: A time offset to apply to all application times. This might be required for
                the case that the simulation places one item after another on the carrier, such that the forces are
                applied after all items have been placed.

        Returns:
            A `ForceApplicationProfile` instance representing a dummy force application profile.
        """
        relative_forces = get_dummy_relative_force_applications(time_offset=application_time_offset)
        absolute_forces = [
            AbsoluteForceApplication.from_relative_force_application(
                relative_force_application=relative_force, magnitude=magnitude, target=target
            )
            for relative_force in relative_forces
        ]
        return ForceApplicationProfile(absolute_forces)

    @staticmethod
    def get_sin_dummy_profile(
        magnitude: float, target: str, application_time_offset: float = 0.0
    ) -> ForceApplicationProfile:
        """
        Returns a sine wave dummy force application profile.

        Args:
            magnitude: The reference force magnitude in Newton.
            target: The name of the body to that the forces of this profile are applied.
            application_time_offset: A time offset to apply to all application times. This might be required for
                the case that the simulation places one item after another on the carrier, such that the forces are
                applied after all items have been placed.

        Returns:
            A `ForceApplicationProfile` instance representing a sine wave dummy force application profile.
        """

        relative_forces = get_sin_dummy_relative_force_applications(time_offset=application_time_offset)
        absolute_forces = [
            AbsoluteForceApplication.from_relative_force_application(
                relative_force_application=relative_force, magnitude=magnitude, target=target
            )
            for relative_force in relative_forces
        ]
        return ForceApplicationProfile(absolute_forces)

    @staticmethod
    def get_radial_profile(
        magnitude: float, target: str, application_time_offset: float = 0.0
    ) -> ForceApplicationProfile:
        """
        Returns a radial force application profile.

        Args:
            magnitude: The reference force magnitude in Newton.
            target: The name of the body to that the forces of this profile are applied.
            application_time_offset: A time offset to apply to all application times. This might be required for
                the case that the simulation places one item after another on the carrier, such that the forces are
                applied after all items have been placed.

        Returns:
            A `ForceApplicationProfile` instance representing a radial force application profile.
        """

        relative_forces = get_radial_relative_force_applications(time_offset=application_time_offset)
        absolute_forces = [
            AbsoluteForceApplication.from_relative_force_application(
                relative_force_application=relative_force, magnitude=magnitude, target=target
            )
            for relative_force in relative_forces
        ]
        return ForceApplicationProfile(absolute_forces)
