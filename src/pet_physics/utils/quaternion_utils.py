"""This module contains utils for working with quaternions."""

import numpy as np

from pet_physics.type_alias_definition import Vector3d, Vector4d


def get_normalized_vector(vector: Vector3d | np.ndarray) -> np.ndarray:
    """Returns the same vector but with norm 1.

    Args:
        vector: The vector that is normalized.

    Returns:
        The normalized vector.
    """
    return np.array(vector, dtype=float) / np.linalg.norm(vector)


def create_rotation_quaternion(angle_deg: float, rotation_axis: Vector3d) -> np.ndarray:
    """Create a quaternion for rotation around a specified axis.

    Args:
        angle_deg: The rotation angle in degrees.
        rotation_axis: The rotation axis, e.g., `(0, 0, 1)` represents a rotation around the z-axis.

    Returns:
        Quaternion with its components `(w, x, y, z)`.
    """
    # convert to radians and normalize rotation axis
    angle_rad = np.radians(angle_deg)
    unit_rotation_axis = get_normalized_vector(rotation_axis)

    # calculate quaternion components
    w = np.cos(angle_rad / 2)
    x, y, z = np.sin(angle_rad / 2) * unit_rotation_axis

    return np.array([w, x, y, z])


def rotate_vector_by_quaternion(
    vector: Vector3d | np.ndarray, quaternion: np.ndarray = np.array([0, 0, 0, 0]), normalize_vectors: bool = True
):
    """Rotate a vector by a given quaternion using NumPy.

    Args:
        vector: The vector that is rotated, e.g., a unit normal vector.
        quaternion: Quaternion as `(w, x, y, z)`, where `w` is the scalar part.
        normalize_vectors: Whether to normalize the input vector and the output vector.

    Returns:
        The rotated vector.
    """
    unit_quaternion = np.array(quaternion, dtype=float)
    if normalize_vectors:
        vector = get_normalized_vector(vector)

    # extract components
    w, x, y, z = unit_quaternion

    # Quaternion rotation formula using vector operations
    # v' = q * v * q^-1 can be expanded to the formula below
    # For a normalized quaternion, this simplifies calculations
    # This is a more efficient formula that avoids full quaternion multiplication
    vector_part_quaternion = np.array([x, y, z])
    t = 2 * np.cross(vector_part_quaternion, vector)
    rotated_vector = vector + w * t + np.cross(vector_part_quaternion, t)

    if normalize_vectors:
        rotated_vector = get_normalized_vector(rotated_vector)

    return rotated_vector


def oriented_size(size: Vector3d | np.ndarray, quat: np.ndarray | Vector4d) -> np.ndarray:
    """Compute the oriented, i.e., axis-aligned bounding box (AABB), size of a box with original axis-aligned size
    after rotation by quaternion 'quat'.

    Args:
        size: The original axis-aligned size of the box, e.g., `(sx, sy, sz)`.
        quat: The quaternion representing the rotation, e.g., `(w, x, y, z)`.

    Returns:
        The size of the box after rotation, i.e., the size of the AABB that contains the rotated box.
    """

    sx, sy, sz = size
    hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5

    # Half-extents along local axes
    ex = rotate_vector_by_quaternion(vector=(hx, 0, 0), quaternion=quat, normalize_vectors=False)
    ey = rotate_vector_by_quaternion(vector=(0, hy, 0), quaternion=quat, normalize_vectors=False)
    ez = rotate_vector_by_quaternion(vector=(0, 0, hz), quaternion=quat, normalize_vectors=False)

    # Sum absolute contributions
    new_x = 2 * (abs(ex[0]) + abs(ey[0]) + abs(ez[0]))
    new_y = 2 * (abs(ex[1]) + abs(ey[1]) + abs(ez[1]))
    new_z = 2 * (abs(ex[2]) + abs(ey[2]) + abs(ez[2]))

    return np.array([new_x, new_y, new_z])
