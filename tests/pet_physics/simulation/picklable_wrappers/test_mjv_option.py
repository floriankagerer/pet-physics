"""Tests for the MjvOption class."""

import pickle

from pet_physics.simulation.picklable_wrappers.mjv_option import MjvOption


def test_pickle():
    option = MjvOption()

    pickled_option = pickle.dumps(option)
    unpickled_option = pickle.loads(pickled_option)

    assert all(option.geomgroup == unpickled_option.geomgroup)
