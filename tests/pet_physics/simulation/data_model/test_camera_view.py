"""Tests for `CameraView`."""

import dataclasses

import numpy as np
import pytest

from pet_physics.simulation.data_model.camera_view import CameraView


def test_camera_view_stores_all_fields() -> None:
    """Constructing a `CameraView` should store all provided fields unchanged."""
    lookat = np.array([1.0, 2.0, 3.0])

    camera_view = CameraView(azimuth=10.0, elevation=-20.0, distance=2.5, lookat=lookat)

    assert camera_view.azimuth == 10.0
    assert camera_view.elevation == -20.0
    assert camera_view.distance == 2.5
    assert list(camera_view.lookat) == [1.0, 2.0, 3.0]


def test_camera_view_is_immutable() -> None:
    """`CameraView` is a frozen dataclass; mutating a field should raise `FrozenInstanceError`."""
    camera_view = CameraView(azimuth=0.0, elevation=0.0, distance=1.0, lookat=np.zeros(3))

    with pytest.raises(dataclasses.FrozenInstanceError):
        camera_view.azimuth = 5.0
