"""Tests for `RelativeForceApplication` and `AbsoluteForceApplication`."""

import pytest

from pet_physics.data_model.simulation.force_application import AbsoluteForceApplication, RelativeForceApplication


@pytest.mark.parametrize(
    ("force_application_class", "extra_kwargs"),
    [
        (RelativeForceApplication, {"percentage_vector": (0.5, 0.0, 0.0)}),
        (AbsoluteForceApplication, {"force_vector": (10.0, 0.0, 0.0), "target": "box_a"}),
    ],
    ids=["relative", "absolute"],
)
def test_end_time_is_start_time_plus_duration(force_application_class: type, extra_kwargs: dict) -> None:
    """`end_time` should equal `start_time + duration` for both force application types."""
    force_application = force_application_class(start_time=2.0, duration=3.5, **extra_kwargs)

    assert force_application.end_time == 5.5


def test_from_relative_force_application_scales_percentage_vector_by_magnitude() -> None:
    """The absolute force vector should be the relative percentage vector scaled by the given magnitude."""
    relative = RelativeForceApplication(start_time=1.0, duration=2.0, percentage_vector=(0.5, -0.25, 1.0))

    absolute = AbsoluteForceApplication.from_relative_force_application(
        relative_force_application=relative, magnitude=100.0, target="box_a"
    )

    assert absolute.force_vector == [50.0, -25.0, 100.0]
    assert absolute.start_time == 1.0
    assert absolute.duration == 2.0
    assert absolute.target == "box_a"
