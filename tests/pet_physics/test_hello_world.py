"""Tests the module `hello_world`."""

from pet_physics.hello_world import get_one


def test_get_one() -> None:
    """Tests the function get one."""
    assert get_one() == 1
