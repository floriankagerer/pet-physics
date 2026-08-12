"""Detects box drops during simulation using recorded pose history.

This module provides `DroppedBodyDuringSimulationDetector`, which inspects the poses recorded during a simulation run
to determine whether a box fell off the carrier, and if so, at which point in time.
"""

import structlog

from pet_physics.data_model.dropped_body import DroppedBody
from pet_physics.data_model.physical_quantities.pose import Pose
from pet_physics.simulation.drop_detection.base_drop_detector import BaseDropDetector
from pet_physics.simulation.drop_detection.drop_detection_core import (
    is_body_bottom_side_below_z_coordinate_that_defines_floor_contact,
)
from pet_physics.simulation.physical_quantities.history.pose_history import PoseHistory
from pet_physics.type_alias_definition import Size3d
from pet_physics.utils.quaternion_utils import oriented_size

logger = structlog.get_logger(__name__)

# TODO(florian): Exclude the time before a teleport when detecing box drops.


class DroppedBodyDuringSimulationDetector(BaseDropDetector):
    """A detector for boxes that fell off the pallet during a simulation run.

    A box is considered as dropped if
    - the body's bottom side is at least some distance below the top side of the carrier.

    Note that the *oriented size* represents the size of the axis-aligned bounding box (AABB) of the body, where
    the AABB is the smallest bounding box that contains the (rotated) body and is aligned with the coordinate axes.
    """

    @staticmethod
    def _get_index_last_recorded_pose(body_pose_history: list[Pose]) -> int:
        """Returns the index of the body's position that was recorded last.

        Note that this search assumes that the body poses are initialized with `Pose(pos=None, quat=None)`.

        Args:
            The recorded poses of a body. If no pose has been recorded, the position value of the pose is `None`.
        """
        for index_body_pose_history in range(len(body_pose_history)):
            index_last_recorded_pose = -(1 + index_body_pose_history)
            last_recorded_position = body_pose_history[index_last_recorded_pose].pos
            if last_recorded_position is not None:
                return index_last_recorded_pose

    @staticmethod
    def _shorten_body_pose_history_to_include_only_recorded_poses(body_pose_history: list[Pose]) -> list[Pose]:
        """Trims the trailing, not-yet-recorded poses from the body's pose history.

        Args:
            body_pose_history: The recorded poses of a body. If no pose has been recorded, the position
                value of the pose is `None`.

        Returns:
            The body pose history without trailing unrecorded poses.
        """
        # try to shorten body pose history (add +1 to last index to include the last recorded pose)
        index_last_recorded_pose = DroppedBodyDuringSimulationDetector._get_index_last_recorded_pose(body_pose_history)
        shortened_body_pose_history = body_pose_history[: index_last_recorded_pose + 1]
        return shortened_body_pose_history

    @staticmethod
    def _sort_dropped_bodies_by_drop_timestamp(dropped_bodies: list[DroppedBody]) -> list[DroppedBody]:
        """Orders dropped bodies chronologically, starting with the one that fell first.

        Args:
            dropped_bodies: The list of dropped bodies to sort.

        Returns:
            The sorted list of dropped bodies, starting with the body that dropped first.
        """
        sorted_dropped_bodies = sorted(dropped_bodies, key=lambda x: x.drop_timestamp)
        return sorted_dropped_bodies

    def _detect_dropped_body_including_drop_timestamp(
        self, body_name: str, body_size: Size3d, body_pose_history: list[Pose]
    ) -> DroppedBody | None:
        """Detects whether a body fell off the carrier during the simulation.

        If the body is detected as dropped, the index of the pose at which it dropped is recorded as the drop
        timestamp.

        Args:
            body_name: The name of the body to check.
            body_size: The size of the body.
            body_pose_history: The recorded poses of the body.

        Returns:
            The dropped body with its drop timestamp if a body is detected as dropped, `None` otherwise.
        """
        for index_recorded_pose, body_pose in enumerate(body_pose_history):
            position_center_of_mass = body_pose.pos
            quaternion = body_pose.quat

            body_oriented_size = oriented_size(size=body_size, quat=quaternion)

            if is_body_bottom_side_below_z_coordinate_that_defines_floor_contact(
                position_center_of_mass=position_center_of_mass,
                oriented_size=body_oriented_size,
                z_coordinate_defining_floor_contact=self.z_coordinate_defining_floor_contact,
            ):
                dropped_body = DroppedBody(name=body_name, drop_timestamp=index_recorded_pose)
                return dropped_body

    def detect(self, body_name_to_size_mapping: dict[str, Size3d], pose_history: PoseHistory) -> list[DroppedBody]:
        """Detects boxes that fell off the carrier during the simulation.

        For each detected body, the recorded drop timestamp corresponds to the index of the pose at which the
        body was first found to have fallen.

        Args:
            body_name_to_size_mapping: The dimensions of the boxes in the simulation. The keys of
                the dict are the names of the boxes as they are specified in the MJCF, and the values are the
                dimensions of the boxes.
            pose_history: The history of the poses of the bodies during the simulation.

        Returns:
            A sorted list of the bodies that dropped during the simulation, starting with the body
                that dropped first.
        """
        dropped_bodies: list[DroppedBody] = []

        for body_name, body_pose_history in pose_history.body_name_with_values():
            body_size = body_name_to_size_mapping[body_name]

            shortened_body_pose_history = self._shorten_body_pose_history_to_include_only_recorded_poses(
                body_pose_history
            )

            dropped_body = self._detect_dropped_body_including_drop_timestamp(
                body_name=body_name,
                body_size=body_size,
                body_pose_history=shortened_body_pose_history,
            )
            if dropped_body is not None:
                dropped_bodies.append(dropped_body)

        sorted_dropped_bodies = self._sort_dropped_bodies_by_drop_timestamp(dropped_bodies)
        msg = f"Dropped bodies during simulation: {','.join([str(body) for body in sorted_dropped_bodies])}"
        logger.info(msg)

        return sorted_dropped_bodies
