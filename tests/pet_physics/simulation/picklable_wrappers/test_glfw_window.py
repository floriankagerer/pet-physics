"""Tests for the GLFWWindow class."""

import pickle

from pet_physics.simulation.picklable_wrappers.glfw_window import GLFWWindow


def test_pickle():
    glfw_window = GLFWWindow()

    pickled_window = pickle.dumps(glfw_window)
    unpickled_window = pickle.loads(pickled_window)
