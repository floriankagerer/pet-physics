"""Contains a list of dummy relative force applications."""

from pet_physics.data_model.simulation.force_application import RelativeForceApplication


def get_dummy_relative_force_applications(time_offset: float = 0.0) -> list[RelativeForceApplication]:
    """
    Provides a list of relative force applications.

    Args:
        time_offset: A time offset to apply to all application times. This might be required for the case that
            the simulation places one item after another on the carrier, such that the forces are applied after
            all items have been placed.

    Returns:
        A list of `RelativeForceApplication`.
    """
    forces = [
        RelativeForceApplication(
            start_time=1.0 + time_offset,
            duration=0.15,
            percentage_vector=(0.9, 0.1, 0.0),
        ),
        RelativeForceApplication(
            start_time=1.1 + time_offset,
            duration=0.15,
            percentage_vector=(-0.4, -0.1, 0.0),
        ),
        RelativeForceApplication(
            start_time=2.0 + time_offset,
            duration=0.15,
            percentage_vector=(-0.95, -0.1, 0.1),
        ),
        RelativeForceApplication(
            start_time=3.0 + time_offset,
            duration=0.15,
            percentage_vector=(0.55, 0.2, 0.1),
        ),
        RelativeForceApplication(
            start_time=4.0 + time_offset,
            duration=0.15,
            percentage_vector=(-0.75, -0.3, 0.15),
        ),
        RelativeForceApplication(
            start_time=5.0 + time_offset,
            duration=0.15,
            percentage_vector=(-1.0, -0.25, 0.1),
        ),
        RelativeForceApplication(
            start_time=6.0 + time_offset,
            duration=0.15,
            percentage_vector=(1.1, 0.2, 0.1),
        ),
        RelativeForceApplication(
            start_time=7.0 + time_offset,
            duration=0.15,
            percentage_vector=(1.2, 0.2, 0.1),
        ),
        RelativeForceApplication(
            start_time=8.0 + time_offset,
            duration=0.15,
            percentage_vector=(1.2, 0.2, 10.0),
        ),
    ]

    return forces
