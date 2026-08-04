"""This module tests the module teleport in the data model."""

import pytest

from pet_physics.data_model.teleport import Teleport

TARGET_POSITION = (0.3, 0.2, 0.1)
"""A target position of a teleport."""
INITIAL_POSITION = (1.0, 1.0, 1.0)
"""An initial position of a teleport."""
EXPECTED_DELTA = (-0.7, -0.8, -0.9)
"""The expected delta position with the previously given target and initial position, respectively."""


@pytest.fixture
def teleport_test() -> Teleport:
    return Teleport(name="teleport_test", target_position=TARGET_POSITION, initial_position=INITIAL_POSITION)


def test_delta_position(teleport_test: Teleport) -> None:
    """Tests whether the calculation of the delta position is done correctly."""
    assert teleport_test.delta_position == EXPECTED_DELTA
