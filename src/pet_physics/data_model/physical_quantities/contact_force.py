"""This module is responsible for tracking the contact forces and the related contact objects in MuJoCo."""

from dataclasses import dataclass

import numpy as np

from pet_physics.wrapper.mj_contact_wrapper import MjContactWrapper


@dataclass
class ContactForce:
    """Instances of this class represent a contact force in MuJoCo. You can access the contact that belongs to this
    contact force and its value. Note that class does not take care of the body the contact force belongs to.

    Attributes:
        contact: The related contact object of the contact force.
        value: The value of the contact force.
    """

    contact: MjContactWrapper
    value: np.ndarray

    @property
    def value_z(self) -> float:
        """The value of the contact force in z-direction."""
        return self.value[2]

    @property
    def penetration(self) -> float:
        """The penetration due to the contact force."""
        return self.contact.distance
