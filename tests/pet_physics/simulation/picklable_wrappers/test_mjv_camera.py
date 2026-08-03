"""Tests for the MjvCamera class."""

import pickle

from pet_physics.simulation.picklable_wrappers.mjv_camera import MjvCamera


def test_pickle():
    camera = MjvCamera()

    pickled_camera = pickle.dumps(camera)
    unpickled_camera = pickle.loads(pickled_camera)

    assert camera.type == unpickled_camera.type
