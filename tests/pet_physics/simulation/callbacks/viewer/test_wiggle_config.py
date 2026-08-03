"""Tests for `WiggleConfig`."""

import pytest

from pet_physics.simulation.callbacks.viewer.wiggle_config import (
    DEFAULT_VEL_X,
    DEFAULT_VEL_Y,
    DEFAULT_VEL_Z,
    WiggleConfig,
)

_DEFAULTS = {"vel_x": DEFAULT_VEL_X, "vel_y": DEFAULT_VEL_Y, "vel_z": DEFAULT_VEL_Z}


def test_default_velocities_match_module_constants() -> None:
    """A freshly constructed `WiggleConfig` should expose the default velocities."""
    config = WiggleConfig()

    assert config.vel_x == DEFAULT_VEL_X
    assert config.vel_y == DEFAULT_VEL_Y
    assert config.vel_z == DEFAULT_VEL_Z


@pytest.mark.parametrize(
    ("method_name", "attribute", "expected_delta"),
    [
        ("increase_velocity_x", "vel_x", 2),
        ("decrease_velocity_x", "vel_x", -2),
        ("increase_velocity_y", "vel_y", 2),
        ("decrease_velocity_y", "vel_y", -2),
        ("increase_velocity_z", "vel_z", 2),
        ("decrease_velocity_z", "vel_z", -2),
    ],
)
def test_velocity_change_updates_only_targeted_axis(method_name: str, attribute: str, expected_delta: int) -> None:
    """Each increment/decrement method should change only its own axis, by exactly 2 units."""
    config = WiggleConfig()

    getattr(config, method_name)()

    assert getattr(config, attribute) == _DEFAULTS[attribute] + expected_delta
    for other_attribute in (name for name in _DEFAULTS if name != attribute):
        assert getattr(config, other_attribute) == _DEFAULTS[other_attribute]
