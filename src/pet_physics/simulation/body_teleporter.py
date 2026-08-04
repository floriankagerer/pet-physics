"""This module is responsible for applying the teleports to the correct object in the MuJoCo simulation."""

from copy import deepcopy

import mujoco
import numpy as np
import structlog

from pet_physics.data_model.evaluation.stability_check import StabilityCheck
from pet_physics.data_model.teleport import Teleport
from pet_physics.simulation.mujoco_lookup_helpers import (
    get_body_id,
    get_body_names_in_model,
    get_joint_start_address_of_body,
    get_position_of_body,
)

logger = structlog.get_logger(__name__)


class BodyTeleporter:
    """This class is responsible for applying the teleports to the bodies in a MuJoCo simulation. With teleport we
    mean the sudden change of a body's position in the simulation.

    When speaking about **bodies** in this module, we mean the body objects that are defined by the `<body>` tag
    in the mujoco_model.xml file.

    It is important to say that there are three different position that belong to a body:

    (1) `<body .... pos="0.3 0.2 0.1" />`: This is the position as it is defined in the mujoco_model.xml file and
    defines the initial position of a body. The body is initially placed in this position. Due to gravity this can
    change during simulation.

    (2) During runtime, the position of a body may change. To access the latest position of a body, you need the
    `mujoco.MjData` object that belongs to the `mujoco.MjModel`. The current position of a body, relative to its parent
    body, i.e., the tag in that `<body ... />` is placed, is accessed by `data.xpos[body_id]`.

    (3) To update a position of a body during runtime, we again need the `mujoco.MjData` object and the joint id, i.e.,
    the start address of a body's joints in `data.qpos`.
    The specific update depends on what type of joints and how many of them (and in what order) the body contains.
    In general, it is not the case that updating the first 3 positions that correspond to the body in the `data.qpos`
    vector will update the XYZ cartesian coordinates.
    """

    def __init__(self, model: mujoco.MjModel, stability_check: StabilityCheck) -> None:
        """The constructor.

        Args:
            model: The MuJoCo model.
            stability_check: The stability check object.
        """

        body_names = get_body_names_in_model(model, ignore_private_bodies=True, ignore_additional_bodies=["world"])
        """All interesting body names that are defined in the model."""

        self._joint_start_address_of = self._get_mapper_body_name_to_joint_start_address_of_body(model, body_names)
        """This dictionary maps the name of a body to the start adress of its joints in `data.qpos`."""

        self._body_id_of = self._get_mapper_body_name_to_body_id(model, body_names)
        """This dictionary maps the name of a body to its body id."""

        self._initial_positions_of_bodies = self._get_initial_body_positions(model, body_names)
        """Contains the name of each body and its initial position, i.e., the position as it is defined in the 
        model file."""

        self._body_teleports: list[Teleport | list[Teleport]] = []
        """The list of body teleports that are applied in a MuJoCo simulation. When setting this attribute, use the
        property, i.e., `self.body_teleports`!"""

        self._time_last_teleport: float | None = None
        """The simulation time in that the last teleport was applied."""

        self._is_deactivated = stability_check.is_type_static or stability_check.is_type_wiggle
        """Indicates whether the body teleporter is deactivated, i.e., whether body teleports are applied."""

    @property
    def body_teleports(self) -> list[Teleport | list[Teleport]]:
        """The list of body teleports that are applied in a MuJoCo simulation."""
        return self._body_teleports

    @body_teleports.setter
    def body_teleports(self, value: list[Teleport | list[Teleport]]) -> None:
        if value is None:
            logger.warning(f"you assigned `{value}` to attribute 'body_teleports'")
            self._body_teleports = []
        else:
            self._body_teleports = deepcopy(value)

    @property
    def are_all_body_teleports_applied(self) -> bool:
        """Indicates whether all bodies are teleported."""
        n_remaining_teleports_leq_0 = len(self.body_teleports) <= 0
        return n_remaining_teleports_leq_0 or self._is_deactivated

    @property
    def time_last_teleport(self) -> float:
        """The simulation time in that the last teleport was applied."""
        return self._time_last_teleport

    def _get_mapper_body_name_to_joint_start_address_of_body(
        self, model: mujoco.MjModel, body_names: list[str]
    ) -> dict[str, int]:
        """Returns the dictionary that maps from a body name as given in the model file to its joint id.

        Args:
            model: The mujoco model.
            body_names: A list of body names that are added to the dictionary

        Returns:
            The keys are the names of the bodies and the values are the corresponding joint ids of each body.
        """
        return {body_name: get_joint_start_address_of_body(model, body_name) for body_name in body_names}

    def _get_mapper_body_name_to_body_id(self, model: mujoco.MjModel, body_names: list[str]) -> dict[str, int]:
        """Returns the dictionary that maps from a body name as given in the model file to its joint id.

        Args:
            model: The mujoco model.
            body_names: A list of body names that are added to the dictionary

        Returns:
            The keys are the names of the bodies and the values are the corresponding joint ids of each body.
        """
        return {body_name: get_body_id(model, body_name) for body_name in body_names}

    def _get_initial_body_positions(self, model: mujoco.MjModel, body_names: list[str]) -> dict[str, np.ndarray]:
        """Returns a dictionary that maps from a body name as given in the model file to its position as defined there.

        Args:
            model: The mujoco model.
            body_names: A list of body names that are added to the dictionary

        Returns:
            The keys are the names of the bodies and the values are the corresponding position of each body as defined
            in the model file.

        """
        return {name: get_position_of_body(model, name) for name in body_names}

    def _body_names_containing(self, body_name: str) -> list[str]:
        """Returns a list of body names that contain the specified body name.

        This method is useful if the compiler of MuJoCo creates multiple `<body>` objects from, e.g., a single
        `<flexcomp>` object.

        Args:
            body_name: The name of the body as it is defined in the model before compilation.

        Returns:
            All body names that contain the specified `body_name` string.
        """
        body_names = []
        for compiled_body_name in self._joint_start_address_of.keys():
            if (body_name in compiled_body_name) and (compiled_body_name.startswith(body_name)):
                # check whether no other character is in front of substring!
                # otherwise we would teleport ["2_Box_JUICE", "42_Box_JUICE", "52_Box_JUICE"]
                # if body_name = "2_Box_JUICE"
                body_names.append(compiled_body_name)

        return body_names

    def _get_coordinates_in_parent_frame(self, data: mujoco.MjData, body_name: str) -> np.ndarray:
        """Returns the coordinates of the specified body with respect to its parent frame, i.e., the worldbody.
        In other words: this method returns the coordinates of a body in world coordinates.

        **Important.** Use `xpos` in combination with `body_id` to get coordinates during simulation,
        since for soft bodies the values of
        ```
        data.xpos[body_id] != data.qpos[joint_id]
        ```
        even though we use the `joint_id` that belongs to the same body.
        (For rigid bodies, there is no difference.)

        Args:
            data: The data of the MuJoCo simulation.
            body_name: The name of the body as it is defined in the model file.

        Returns:
            The coordinates of the specified body in world coordinates.
        """
        body_id = self._body_id_of[body_name]
        return data.xpos[body_id]

    def _add_delta_to_body_position(self, data: mujoco.MjData, body_name: str, delta: np.ndarray) -> None:
        """Adds the given 3D delta vector to the position components of the joints associated with 
        the specified body in MuJoCo. 

        This method assumes:
        
        (1) The body has associated joints that control its position.\\
        (2) These joints' positions are stored consecutively in `data.qpos`.\\
        (3) The first 3 values in `data.qpos` starting from the body's joint address correspond to XYZ cartesian 
        coordinates.

        The method will modify the position state (`qpos`) by adding the delta vector to these 3 values. 
        Note that this will only correctly update the body's position if the joints are configured to control 
        cartesian movement (e.g., with a free joint or 3 prismatic joints). For other joint configurations, 
        the behavior may not result in the expected cartesian movement
        
        **Important.** Update the position of a body with its `joint_id` and `data.qpos`.

        Args:
            data: The data of the MuJoCo simulation.
            body_name: The name of the body as it is defined in the model file.
            delta: The position delta that is added to the `qpos` attribute of the body.
        """
        joint_start_addr = self._joint_start_address_of[body_name]
        data.qpos[joint_start_addr : joint_start_addr + 3] += delta

    def update_body_position(
        self, data: mujoco.MjData, body_name: str, position_delta: tuple[float, float, float]
    ) -> None:
        """Updates the position of the specified body in the MuJoCo simulation.

        Args:
            data: The data of the MuJoCo simulation.
            body_name: The name of the body as it is defined in the model file.
            position_delta: The delta of the position, i.e., target position minus initial position.
        """
        packing_delta = np.array(position_delta)

        for compiled_body_name in self._body_names_containing(body_name):
            # initial position of body as specified in the loaded .xml file
            initial_position = self._initial_positions_of_bodies[compiled_body_name]
            # current position, i.e., initial position with possible changes due to gravity/forces
            current_position = self._get_coordinates_in_parent_frame(data, compiled_body_name)

            # delta due to forces
            fall_delta = initial_position - current_position

            # the delta that is added to the position
            total_delta = fall_delta + packing_delta
            self._add_delta_to_body_position(data, compiled_body_name, total_delta)

    def pop_teleport(self) -> Teleport | None:
        """Pops the first teleport from the list.

        Returns:
            The first teleport in the list.
        """
        if self._body_teleports:
            return self._body_teleports.pop(0)
        else:
            return None

    def apply_next_teleport(self, data: mujoco.MjData, simulation_time: float) -> None:
        """Applies the first body teleport in the list.

        Args:
            data: The simulation data.
            simulation_time: The current simulation time.
        """
        teleport = self.pop_teleport()
        if teleport is not None:
            if isinstance(teleport, list):
                teleport_list = teleport
            else:
                teleport_list = [teleport]
            for teleport_item in teleport_list:
                self.update_body_position(data, teleport_item.name, teleport_item.delta_position)

            self._time_last_teleport = simulation_time
            if self.are_all_body_teleports_applied:
                logger.info("all items are palletized")

    def set_teleports(self, teleports: list[Teleport], simulation_time: float) -> None:
        """Sets the body teleporter attributes for a new simulation.

        Args:
            teleports: The teleports that are applied in a MuJoCo simulation.
            simulation_time: The current simulation time.
        """
        self.body_teleports = teleports
        self._time_last_teleport = simulation_time

    def is_time_for_teleport(self, simulation_time: float, teleport_every: float) -> bool:
        """Indicates whether it is time to apply the next teleport, if there is any.

        Args:
            simulation_time: The current simulation time.
            teleport_every: The time span between two teleports.

        Returns:
            Indicates whether it is time to apply the next teleport.
        """
        if not self.are_all_body_teleports_applied and (simulation_time - self.time_last_teleport >= teleport_every):
            return True
        else:
            return False
