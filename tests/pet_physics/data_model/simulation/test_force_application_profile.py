"""Tests for `ForceApplicationProfile`."""

import pytest

from pet_physics.data_model.simulation.force_application import AbsoluteForceApplication
from pet_physics.data_model.simulation.force_application_profile import ForceApplicationProfile

_FORCE_A = AbsoluteForceApplication(start_time=0.0, duration=1.0, force_vector=(1.0, 0.0, 0.0), target="box_a")
_FORCE_B = AbsoluteForceApplication(start_time=1.0, duration=1.0, force_vector=(0.0, 1.0, 0.0), target="box_b")


def test_new_profile_without_forces_is_empty() -> None:
    """A `ForceApplicationProfile` constructed without arguments should have no forces."""
    profile = ForceApplicationProfile()

    assert profile.forces == []
    assert profile.number_forces == 0


def test_profile_stores_and_counts_the_given_forces() -> None:
    """`forces` and `number_forces` should reflect the forces passed to the constructor."""
    profile = ForceApplicationProfile([_FORCE_A, _FORCE_B])

    assert profile.forces == [_FORCE_A, _FORCE_B]
    assert profile.number_forces == 2


def test_add_combines_two_profiles_into_a_new_profile_without_mutating_operands() -> None:
    """`+` should return a new profile containing the forces of both operands, leaving both operands unchanged."""
    profile_a = ForceApplicationProfile([_FORCE_A])
    profile_b = ForceApplicationProfile([_FORCE_B])

    combined = profile_a + profile_b

    assert combined.forces == [_FORCE_A, _FORCE_B]
    assert profile_a.forces == [_FORCE_A]
    assert profile_b.forces == [_FORCE_B]


def test_iadd_extends_the_profile_in_place() -> None:
    """`+=` should extend the profile's own force list in place."""
    profile_a = ForceApplicationProfile([_FORCE_A])
    profile_b = ForceApplicationProfile([_FORCE_B])

    profile_a += profile_b

    assert profile_a.forces == [_FORCE_A, _FORCE_B]


def test_add_with_unsupported_type_raises_type_error() -> None:
    """Adding a non-`ForceApplicationProfile` should raise a `TypeError` via `NotImplemented`."""
    profile = ForceApplicationProfile([_FORCE_A])

    with pytest.raises(TypeError):
        _ = profile + "not-a-profile"
