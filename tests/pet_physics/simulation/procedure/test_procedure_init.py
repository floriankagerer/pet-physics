"""Tests __init__.py of the module procedure."""

import pytest

from pet_physics.simulation.procedure import get_simulation_procedure


@pytest.mark.parametrize(
    "name,should_fail",
    [
        ("default", False),
        ("rigid", False),
        ("fails", True),
    ],
)
def test_get_simulation_procedure(name: str, should_fail: bool) -> None:
    """Tests whether the function that returns the simulation procedures works as expected."""
    if not should_fail:
        _ = get_simulation_procedure(name)
    else:
        with pytest.raises(ValueError):
            _ = get_simulation_procedure(name)
