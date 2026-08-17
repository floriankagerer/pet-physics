"""Contains a list of relative force applications, based on sine waves."""

from math import sqrt

from pet_physics.data_model.simulation.force_application import RelativeForceApplication


def get_radial_relative_force_applications(time_offset: float = 0.0) -> list[RelativeForceApplication]:
    """
    Returns a list of relative force applications that represent a radial force application profile. The forces are
    applied in the xy plane, as well as in the xz and yz plane. The application times of the forces are distributed
    over time, such that the forces are applied one after another.

    Args:
        time_offset: A time offset to apply to all application times. This might be required for the case that
            the simulation places one item after another on the carrier, such that the forces are applied after
            all items have been placed.

    Returns:
        A list of `RelativeForceApplication` instances representing a radial force application profile.
    """

    forces = [
        # radial forces in xy plane
        RelativeForceApplication(start_time=time_offset + 0.0, duration=0.03, percentage_vector=(sqrt(2), 0, 0.1)),
        RelativeForceApplication(start_time=time_offset + 0.3, duration=0.03, percentage_vector=(1, 1, 0.1)),
        RelativeForceApplication(start_time=time_offset + 0.6, duration=0.03, percentage_vector=(0, sqrt(2), 0.1)),
        RelativeForceApplication(start_time=time_offset + 0.9, duration=0.03, percentage_vector=(-1, 1, 0.1)),
        RelativeForceApplication(start_time=time_offset + 1.2, duration=0.03, percentage_vector=(-sqrt(2), 0, 0.1)),
        RelativeForceApplication(start_time=time_offset + 1.5, duration=0.03, percentage_vector=(-1, -1, 0.1)),
        RelativeForceApplication(start_time=time_offset + 1.8, duration=0.03, percentage_vector=(0, -sqrt(2), 0.1)),
        RelativeForceApplication(start_time=time_offset + 2.1, duration=0.03, percentage_vector=(1, -1, 0.1)),
        # forces in xz and yz plane
        RelativeForceApplication(start_time=time_offset + 3.1, duration=0.03, percentage_vector=(1, 0, 1)),
        RelativeForceApplication(start_time=time_offset + 3.4, duration=0.03, percentage_vector=(0, 1, 1)),
    ]

    return forces
