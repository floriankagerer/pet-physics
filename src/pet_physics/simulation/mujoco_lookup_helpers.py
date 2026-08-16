"""Utility functions for querying MuJoCo model and simulation data.

Provides helpers for resolving geometry and body identifiers by name or id,
filtering contacts by geometry, and accessing joint position addresses in
`data.qpos`.
"""

from __future__ import annotations

from typing import Optional

import mujoco
import numpy as np


def name_of_geom_id(model: mujoco.MjModel, geom_id: int) -> str:
    """Returns the name of the geometry, based on its id.

    Args:
        model: The MuJoCo model this geometry belongs to.
        geom_id: The id of the geometry.

    Returns:
        The name of the geometry as defined in the model.
    """
    return mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, geom_id)


def id_of_geom_name(model: mujoco.MjModel, geom_name: str) -> int:
    """Returns the id of the geometry, based on its name.

    Args:
        model: The MuJoCo model this geometry belongs to.
        geom_name: The name of the geometry.

    Returns:
        The id of the geometry as defined in the model.
    """
    return mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, geom_name)


def get_contacts_of_geometry(
    model: mujoco.MjModel, contacts: list[mujoco.MjContact], geom_name: Optional[str] = None
) -> list[tuple[int, mujoco.MjContact]]:
    """Filters contacts by geometry name and returns them with their original indices.

    Args:
        model: The model of the simulation.
        contacts: All contacts that occurred in the simulation.
        geom_name: The name of the geometry to filter by. If `None`, all contacts are returned.

    Returns:
        A list of tuples where the first element is the index of the contact in the original list and the second element
        is the matching `MjContact` object.
    """
    if geom_name is None:
        return [(c_idx, c) for c_idx, c in enumerate(contacts)]

    else:
        geom_id = id_of_geom_name(model, geom_name)
        return [(c_idx, c) for c_idx, c in enumerate(contacts) if c.geom1 == geom_id or c.geom2 == geom_id]


def get_body_names_in_model(
    model: mujoco.MjModel, ignore_private_bodies: bool = True, ignore_additional_bodies: list[str] = ["world"]
) -> list[str]:
    """The body names present in a given model.

    Args:
        model: The model of the simulation.
        ignore_private_bodies: If `True`, bodies with a leading underscore are excluded.
        ignore_additional_bodies: A list of body names to explicitly exclude from the result.

    Returns:
        A list of body names available in the model.
    """
    n_bodies = model.nbody
    body_names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(n_bodies)]
    if ignore_private_bodies:
        body_names = [body_name for body_name in body_names if body_name[0] != "_"]

    body_names = [body_name for body_name in body_names if body_name not in ignore_additional_bodies]

    return body_names


def get_body_id(model: mujoco.MjModel, body_name: str) -> int:
    """Returns the body id of the body with the given name.

    Args:
        model: The model of the simulation.
        body_name: The name of the body as defined in the model.

    Returns:
        The id of the body in the model.
    """
    return mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, body_name)


def get_geom_names_of_body(model: mujoco.MjModel, body_name: str) -> list[str]:
    """The names of all geometries associated with the given body.

    Args:
        model: The MuJoCo model containing the body and geometry definitions.
        body_name: The name of the body as defined in the model.

    Returns:
        A list of geometry names belonging to the specified body.
    """
    body_id = get_body_id(model, body_name)

    # Collect all geoms associated with this body
    geom_names = []
    for geom_id in range(model.ngeom):
        if model.geom_bodyid[geom_id] == body_id:
            geom_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, geom_id)
            geom_names.append(geom_name)

    return geom_names


def get_joint_start_address_of_body(model: mujoco.MjModel, body_name: str) -> int:
    """Returns the start address in `data.qpos` for the given body.

    This address is used, e.g., to update the `qpos` of this body.

    Reference: https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel
    ```
    # body_jntadr: represents the start address of joints; -1 indicates no joints
    # jnt_qposadr: start address in `qpos` for joint's data
    ```

    Args:
        model: The model of the simulation.
        body_name: The name of the body as defined in the model.

    Returns:
        The start address in `data.qpos` for the given body.

    Example:
        ```
        joint_start_addr = get_joint_start_address_of_body(model, "demo_box")
        position = [1.0, 1.0, 1.0]
        data.qpos[joint_start_addr : joint_start_addr + 3] = np.array(position)
        ```
    """
    body_id = get_body_id(model, body_name)
    return model.jnt_qposadr[model.body_jntadr[body_id]]


def get_position_of_body(model: mujoco.MjModel, body_name: str) -> np.ndarray:
    """Returns the position of a body as it is specified in the model.

    Args:
        model: The model of the simulation.
        body_name: The name of the body as defined in the model.

    Returns:
        The position of the body as a numpy array.
    """
    return model.body(name=body_name).pos


def get_body_contacts(model: mujoco.MjModel, data: mujoco.MjData) -> set[tuple[str, str]]:
    """Returns a set of tuples containing the names of geometries that collide.

    Args:
        model: The model of the simulation.
        data: The simulation data containing current contact information.

    Returns:
        A set of 3-tuples `(geom1_name, geom2_name, geom_on_top)` for each contact, where `geom_on_top` is the
        geometry with the upward contact normal.
    """
    body_contacts = set()

    for contact in data.contact:
        geom1 = contact.geom1
        geom2 = contact.geom2

        geom1_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, geom1)
        geom2_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, geom2)

        # which geom is on top
        normal = contact.frame[0:3]

        if normal[2] > 0:
            geom_on_top = contact.geom2
        else:
            geom_on_top = contact.geom1

        geom_on_top = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, geom_on_top)

        body_contacts.add((geom1_name, geom2_name, geom_on_top))

    return body_contacts
