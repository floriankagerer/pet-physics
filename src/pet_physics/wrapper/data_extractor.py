"""
This module extracts the desired quantites from the MuJoCo data object.
For details, see https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#data
"""

import mujoco
import numpy as np


class DataExtractor:
    """This class is responsible for accessing the correct entries in the MuJoCo data object."""

    @staticmethod
    def simulation_time(data: mujoco.MjData) -> float:
        """Returns the current simulation time."""
        return data.time

    @staticmethod
    def number_contacts(data: mujoco.MjData) -> int:
        """Returns the number of detected contacts in a simulation."""
        return data.ncon

    @staticmethod
    def velocity(data: mujoco.MjData) -> np.ndarray:
        """Returns the velocity."""
        return data.qvel[:]

    @staticmethod
    def acceleration(data: mujoco.MjData) -> np.ndarray:
        """Returns the acceleration."""
        return data.qacc[:]

    @staticmethod
    def detected_contacts(data: mujoco.MjData) -> list[mujoco.MjContact]:
        """Returns a list of all detected contacts.

        Returns:
            contacts: All contacts that were detected.
        """
        return data.contact

    @staticmethod
    def contact_force(model: mujoco.MjModel, data: mujoco.MjData, contact_index: int) -> np.ndarray:
        """
        Extracts the contact force of the requested contact in the current simulation step.

        Args:
            model: The model in the MuJoCo simulation.
            data: The corresponding data in the MuJoCo simulation.
            contact_index: The index of the contact that we are interested in as stored in the MuJoCo data.

        Returns:
            force_and_torque: The force and torque of the requested contact.
        """
        force_and_torque = np.zeros(6)
        mujoco.mj_contactForce(model, data, contact_index, force_and_torque)
        return force_and_torque
