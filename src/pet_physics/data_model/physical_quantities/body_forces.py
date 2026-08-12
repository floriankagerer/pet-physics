"""This module is a convenience class for gathering forces that belong to a body."""

from pet_physics.data_model.physical_quantities.contact_force import ContactForce


class BodyForces:
    """This class is responsible for tracking forces of a MuJoCo body, i.e., a `<body>` object, in a single step
    during a simulation.
    """

    def __init__(self, body_name: str, geom_names: list[str]) -> None:
        """The constructor of this class.

        Args:
            body_name: The name of the body as it is specified in the MJCF.
            geom_names: The names of all geometries that belong to this body.
        """

        self._body_name = body_name
        """The name of the body as it is specified in the MJCF."""
        self._geoms_of_body = geom_names
        """The names of all geometries that belong to this body."""
        self._contact_forces: list[ContactForce] = []
        """All contact forces that act on this body in one simulation step."""

    @property
    def body(self) -> str:
        """The name of the body as it is specified in the MJCF."""
        return self._body_name

    @property
    def contact_forces(self) -> list[ContactForce]:
        """All contact forces that act on this body in one simulation step."""
        return self._contact_forces

    @property
    def n_contacts(self) -> int:
        """The amount of contacts points, i.e., the number of contact forces, this body has in one simulation step."""
        return len(self._contact_forces)

    @property
    def contact_forces_at_bottom(self) -> list[ContactForce]:
        """All contact forces that act at the bottom of this body.

        We know that a contact force acts at the bottom of a body if the geometry of this body is the upper geometry
        of the contact.
        """
        contact_forces_at_bottom = []
        for contact_force in self._contact_forces:
            if contact_force.contact.geom_on_top in self._geoms_of_body:
                contact_forces_at_bottom.append(contact_force)

        return contact_forces_at_bottom

    @property
    def contact_forces_on_top(self) -> list[ContactForce]:
        """All contact forces that act at on top of this body.

        We know that a contact force acts on top of a body if the geometry of this body is the lower geometry
        of the contact.
        """
        contact_forces_on_top = []
        for contact_force in self._contact_forces:
            if contact_force.contact.geom_at_bottom in self._geoms_of_body:
                contact_forces_on_top.append(contact_force)

        return contact_forces_on_top

    @property
    def sum_contact_forces_z_bottom(self) -> float:
        """Returns the sum of the z-value of all contact forces that act on the bottom of the body."""
        sum_z_force = 0.0

        for contact_force in self.contact_forces_at_bottom:
            sum_z_force += contact_force.value_z

        return sum_z_force

    @property
    def sum_contact_forces_z_top(self) -> float:
        """Returns the sum of the z-value of all contact forces that act on top of the body."""
        sum_z_force = 0.0

        for contact_force in self.contact_forces_on_top:
            sum_z_force += contact_force.value_z

        return sum_z_force

    def add_contact_force(self, contact_force: ContactForce) -> None:
        """Adds a contact force that acts on this body in one simulation step.

        Args:
            contact_force: The contact force that is added to the body forces.
        """
        self._contact_forces.append(contact_force)
