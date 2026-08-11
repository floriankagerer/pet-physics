"""This module is responsible for tracking the penetrations of a body."""

from typing import Self

from pet_physics.data_model.physical_quantities.contact_force import ContactForce


class Penetration:
    """This class stores the penetration of a certain body.

    Note that the penetration in MuJoCo can be determined by the distance of a contact. Negative values represent a
    penetration, whereas positive values represent no contact at all. In general, a body can have multiple contacts
    in a single simulation step. In this case, the penetration value of the body is determined by the contact with the
    highest penetration, i.e., the lowest distance value.
    """

    def __init__(self, body_name: str, value: float | None = None) -> None:
        """The constructor of this class.

        Args:
            body_name: The name of the body as it is specified in the MJCF.
            value: The value of the penetration.
        """
        self._body_name = body_name
        """The name of the body as it is specified in the MJCF."""

        self._value = value or 0.0
        """The value of the penetration."""

    @property
    def value(self) -> float:
        """The value of the penetration."""
        return self._value

    def update_value(self, value: float) -> None:
        """Updates the value of the penetration."""
        self._value = min(self._value, value)

    @classmethod
    def from_contact_force(cls, body_name: str, contact_force: ContactForce) -> Self:
        """Creates a `Penetration` object from a contact force.

        Args:
            body_name: The name of the body as it is specified in the MJCF.
            contact_force: The contact force from which the penetration is derived.
        """
        return cls(body_name=body_name, value=contact_force.penetration)
