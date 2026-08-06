"""Tests for the quaternion utils module."""

import numpy as np
import pytest

from pet_physics.utils.quaternion_utils import (
    create_rotation_quaternion,
    get_normalized_vector,
    rotate_vector_by_quaternion,
)

X_AXIS = (1, 0, 0)
"""A 3-tuple that represents the direction of the x-axis."""
Y_AXIS = (0, 1, 0)
"""A 3-tuple that represents the direction of the y-axis."""
Z_AXIS = (0, 0, 1)
"""A 3-tuple that represents the direction of the z-axis."""


@pytest.mark.parametrize(
    "vector, expected_vector",
    [
        ([3.0, 0.0, 0.0], np.array([1.0, 0.0, 0.0])),
        ([1.0, 2.0, 0.0], np.array([1, 2, 0]) / np.sqrt(5)),
        ([1.0, 2.0, 3.0], np.array([1, 2, 3]) / np.sqrt(14)),
        (np.array([1, 2, 42]), np.array([1, 2, 42]) / np.sqrt(1769)),
    ],
)
def test_get_normalized_vector(vector: tuple[float, float, float], expected_vector: np.ndarray) -> None:
    """Tests whether the normalization of a vector correctly works."""
    actual_vector = get_normalized_vector(vector)

    assert np.isclose(actual_vector, expected_vector, atol=1e-4).all()


@pytest.mark.skip("is verified with the tests of `test_rotate_unit_vector_by_quaternion`")
def test_create_rotation_quaternion() -> None:
    raise NotImplementedError("not implemented yet")


@pytest.mark.parametrize(
    "vector, quaternion, normalize_vectors, expected_rotated_vector",
    [
        ([0, 0, 1], create_rotation_quaternion(90, Z_AXIS), True, np.array([0, 0, 1])),
        ([0, 0, 1], create_rotation_quaternion(-90, Z_AXIS), True, np.array([0, 0, 1])),
        ([1, 0, 0], create_rotation_quaternion(90, Z_AXIS), True, np.array([0, 1, 0])),
        ([1, 0, 0], create_rotation_quaternion(180, Z_AXIS), True, np.array([-1, 0, 0])),
        ([1, 0, 0], create_rotation_quaternion(-90, Z_AXIS), True, np.array([0, -1, 0])),
        ([0, 1, 0], create_rotation_quaternion(90, Z_AXIS), True, np.array([-1, 0, 0])),
        ([0, 0, 1], create_rotation_quaternion(90, X_AXIS), True, np.array([0, -1, 0])),
    ],
)
def test_rotate_vector_by_quaternion(
    vector: tuple[float, float, float],
    quaternion: np.ndarray,
    normalize_vectors: bool,
    expected_rotated_vector: np.ndarray,
) -> None:
    """Tests whether the rotation of a vector correctly works.

    For thinking about the expected values of these tests, think about the cartesian coordinate system
    (cf. Regarding the coordinate system, cf. https://en.wikipedia.org/wiki/Three-dimensional_space#Coordinate_systems).
    """
    rotated_vector = rotate_vector_by_quaternion(
        vector=vector, quaternion=quaternion, normalize_vectors=normalize_vectors
    )

    assert np.isclose(rotated_vector, expected_rotated_vector, atol=1e-4).all()
