"""Contains the `MjContactWrapper` class for working with MuJoCo contacts."""

from copy import deepcopy

import mujoco
import numpy as np

from pet_physics.simulation.mujoco_lookup_helpers import name_of_geom_id


class MjContactWrapper:
    """Named geometry and orientation accessors for a `mujoco.MjContact` instance.

    The force direction convention is from `geom1` to `geom2`.
    """

    def __init__(self, mj_contact: mujoco.MjContact, model: mujoco.MjModel) -> None:
        """Wraps a `mujoco.MjContact` with named geometry access.

        Args:
            mj_contact: The MuJoCo contact to wrap. A deep copy is stored internally.
            model: The MuJoCo simulation model used for geometry name lookups.
        """
        self._raw = deepcopy(mj_contact)
        """A deepcopy of the original contact object of MuJoCo."""
        self._model = model
        """The MuJoCo simulation model."""

    def __str__(self) -> str:
        _str = (
            "MjContactWrapper"
            + "("
            + f"pos={np.array_str(self.position, precision=3, suppress_small=True)}, "
            + f"geom={self.name_collision_geometries}, "
            + f"distance={self.distance}"
            + ")"
        )
        return _str

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def collision_geometries(self) -> np.ndarray:
        """The ids of the collision geometries."""
        return self._raw.geom

    @property
    def name_collision_geometries(self) -> np.ndarray:
        """The names of the collision geometries."""
        return [name_of_geom_id(self._model, geom_id) for geom_id in self.collision_geometries.tolist()]

    @property
    def geom1(self) -> int:
        """The id of the first collision geometry."""
        return self._raw.geom1

    @property
    def name_geom1(self) -> str:
        """The name of the `geom1` object."""
        return name_of_geom_id(self._model, self.geom1)

    @property
    def geom2(self) -> int:
        """The id of the second collision geometry."""
        return self._raw.geom2

    @property
    def name_geom2(self) -> str:
        """The name of the `geom2` object."""
        return name_of_geom_id(self._model, self.geom2)

    @property
    def distance(self) -> float:
        """The collision distance."""
        return self._raw.dist

    @property
    def position(self) -> np.ndarray:
        """The position of the contact."""
        return self._raw.pos

    @property
    def unit_normal_vector(self) -> np.ndarray:
        """The normal vector of this contact point."""
        normal_vector = self._raw.frame[0:3]
        unit_normal_vector = normal_vector / np.linalg.norm(normal_vector)
        return unit_normal_vector

    @property
    def tangent1_vector(self) -> np.ndarray:
        """The first tangent vector of the contact frame."""
        t1 = self._raw.frame[3:6]
        norm = np.linalg.norm(t1)
        if norm == 0:
            return t1
        return t1 / norm

    def force_in_world(self, force_in_contact_frame: np.ndarray) -> np.ndarray:
        """Converts a force vector given in the contact frame to world coordinates.

        MuJoCo returns contact forces in the contact frame where the first three
        components correspond to axes described by `frame[0:3]` (normal) and
        `frame[3:6]` (first tangent). The third tangent is the cross product of
        the normal and the first tangent.

        Args:
            force_in_contact_frame: The force vector in the contact frame.

        Returns:
            The force vector in world coordinates.
        """
        n = self.unit_normal_vector
        t1 = self.tangent1_vector
        t2 = np.cross(n, t1)

        f_c = np.asarray(force_in_contact_frame)
        return f_c[0] * n + f_c[1] * t1 + f_c[2] * t2

    def represents_vertical_contact(self) -> bool:
        """Indicates whether this contact is oriented in the vertical direction."""
        vertical_vector = np.array([0, 0, 1])

        cos_angle = np.dot(self.unit_normal_vector, vertical_vector)

        angle_rad = np.arccos(np.clip(cos_angle, -1.0, 1.0))

        # define a tolerance of 45 degrees = pi/4
        tolerance_angle_vertical_contact_rad = np.pi / 4

        return np.abs(angle_rad) < tolerance_angle_vertical_contact_rad

    def _get_geom_ids_top_and_bottom(self) -> tuple[int, int] | tuple[None, None]:
        """Returns the ids of the upper and lower geometries in a vertical contact. If the contact is not vertical,
        returns `None`."""
        if not self.represents_vertical_contact():
            return None, None

        normal = self.unit_normal_vector
        if normal[2] > 0:
            return self.geom2, self.geom1
        else:
            return self.geom1, self.geom2

    @property
    def geom_on_top(self) -> str | None:
        """The name of the upper geometry in a vertical contact.

        `None` if the contact is not vertical.
        """
        top_geom_id, _ = self._get_geom_ids_top_and_bottom()
        if top_geom_id is not None:
            return name_of_geom_id(self._model, top_geom_id)
        else:
            return None

    @property
    def geom_at_bottom(self) -> str | None:
        """The name of the lower geometry in a vertical contact.

        `None` if the contact is not vertical.
        """
        _, bottom_geom_id = self._get_geom_ids_top_and_bottom()
        if bottom_geom_id is not None:
            return name_of_geom_id(self._model, bottom_geom_id)
        else:
            return None
