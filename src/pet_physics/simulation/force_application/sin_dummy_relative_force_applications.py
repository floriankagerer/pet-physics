"""Contains a list of relative force applications, based on sine waves."""

from math import sin

from pet_physics.data_model.simulation.force_application import RelativeForceApplication


def get_sin_dummy_relative_force_applications(time_offset: float = 0.0) -> list[RelativeForceApplication]:
    """
    Provides a sine wave force application profile.

    Args:
        time_offset: A time offset to apply to all application times. This might be required for the case that
            the simulation places one item after another on the carrier, such that the forces are applied after
            all items have been placed.

    Returns:
        A list of `RelativeForceApplication` instances representing a sine wave force application profile.
    """
    forces: list[RelativeForceApplication] = []

    for idx in range(1, 100):
        t = idx / 10.0

        percentage_vector = (sin(t), 0, sin(3 * t))

        forces.append(
            RelativeForceApplication(
                start_time=t + time_offset,
                duration=0.1,
                percentage_vector=percentage_vector,
            )
        )

    return forces
