"""Module for defining coordinate systems in a MuJoCo model."""

from dataclasses import dataclass, field
from typing import Literal
from xml.etree.ElementTree import Element

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.geom import Geom
from pet_physics.data_model.modeling.mjcf.material import Material
from pet_physics.type_alias_definition import Position3d


@dataclass
class CoordinateSystemAssets:
    """Class to represent the materials of a coordinate system in a MuJoCo model.
    This object belongs to the `asset` part of a model.

    Attributes:
        material_x: The material for the x-axis.
        material_y: The material for the y-axis.
        material_z: The material for the z-axis.
    """

    material_x: Material = field(default_factory=lambda: Material(name="arrow.x", rgba=(1, 0, 0, 1)))
    material_y: Material = field(default_factory=lambda: Material(name="arrow.y", rgba=(0, 1, 0, 1)))
    material_z: Material = field(default_factory=lambda: Material(name="arrow.z", rgba=(0, 0, 1, 1)))

    @property
    def materials(self) -> tuple[Material, Material, Material]:
        return (self.material_x, self.material_y, self.material_z)

    def to_xml(self) -> tuple[Element, Element, Element]:
        """Returns the materials for the coordinate system as XML objects.

        Returns:
            The materials as XML elements.
        """
        return tuple(m.to_xml() for m in self.materials)


@dataclass
class CoordinateSystem:
    """Class to represent the coordinate system in a MuJoCo model.
    This object belongs to the `worldbody` part of a model.

    Attributes:
        pos_x: The position of the arrow that represents the x-axis.
        pos_y: The position of the arrow that represents the y-axis.
        pos_z: The position of the arrow that represents the z-axis.
        yaw: The yaw angle of the coordinate system. This is used to rotate the axes around the z-axis.
        name: The name of the coordinate system. (for differentiation if we have more than one)
    """

    pos_x: Position3d = (0, -0.05, 0)
    pos_y: Position3d = (-0.05, 0, 0)
    pos_z: Position3d = (-0.05, -0.05, 0.01)
    yaw: Literal[0, 90, 180, 270] = 0
    name: str = "coordinate_system"

    def to_xml(self) -> tuple[Element, Element, Element]:
        """Returns axes of the coordinate system as XML objects.

        Returns:
            The axes as XML elements.
        """
        return tuple(b.to_xml() for b in self.axes_as_body_objects())

    def axes_as_body_objects(self) -> tuple[Body, Body, Body]:
        """Creates `Body` objects for the MuJoCo model that represent the axes of a coordinate system.

        Returns:
            tuple[Body, Body, Body]: The `Body` object for each axis of the coordinate system.
        """
        shaft_size = (0.01, 0.05)
        shaft_pos = (0, 0, 0.05)
        tip_position = (0, 0, 0.1)
        bodies = []

        # define the axes
        names = ("x", "y", "z")
        orientations = self._get_xyz_orientations(self.yaw)
        body_positions = (self.pos_x, self.pos_y, self.pos_z)

        # create the objects
        for axis_name, axis_orientation, pos in zip(names, orientations, body_positions):
            arrow_body = self._get_body(
                axis_name=axis_name,
                axis_orientation=axis_orientation,
                body_pos=pos,
                shaft_size=shaft_size,
                shaft_pos=shaft_pos,
                tip_pos=tip_position,
            )

            bodies.append(arrow_body)

        return tuple(bodies)

    @staticmethod
    def _get_xyz_orientations(yaw: Literal[0, 90, 180, 270]) -> tuple:
        """Rotates the axis orientations based on the yaw angle.

        Args:
            orientations (tuple): The original orientations of the axes.
            yaw (Literal[0, 90, 180, 270]): The yaw angle to rotate the axes.

        Returns:
            tuple: The rotated orientations of the axes.
        """
        if yaw == 0:
            return (0, 1, 0, 90), (1, 0, 0, -90), None
        elif yaw == 90:
            return (1, 0, 0, -90), (0, 1, 0, -90), None
        elif yaw == 180:
            return (0, 1, 0, -90), (1, 0, 0, 90), None
        elif yaw == 270:
            return (1, 0, 0, 90), (0, 1, 0, 90), None
        else:
            raise ValueError("Yaw must be one of [0, 90, 180, 270].")

    def _get_body(
        self,
        axis_name: Literal["x", "y", "z"],
        axis_orientation: tuple[int, int, int, int] | None,
        body_pos: tuple[float, float, float],
        shaft_size: tuple[float, float],
        shaft_pos: tuple[float, float, float],
        tip_pos: tuple[float, float, float],
    ) -> Body:
        """Returns the `Body` object that represents an arrow of the coordinate system.

        Args:
            axis_name (Literal["x", "y", "z"]): The name of the axis that is inserted into the objects.
            axis_orientation (tuple[int, int, int, int] | None): Defines the orientation of the arrow.
            body_pos (tuple[float, float, float]): The position of the body.
            shaft_size (tuple[float, float]): The radius and the half-heigh of the arrow's shaft.
            tip_pos (tuple[float, float, float]): The position of the cone.

        Returns:
            Body: The arrow as `Body` object.
        """
        object_material = f"arrow.{axis_name}"

        _shaft_geom = Geom(
            name=f"_{self.name}.{axis_name}.shaft",
            type="cylinder",
            size=shaft_size,
            pos=shaft_pos,
            material=object_material,
            mass=None,
            rgba=None,
            solimp=None,
            solref=None,
            contype=0,
            conaffinity=0,
        )
        _tip_geom = Geom(
            name=f"_{self.name}.{axis_name}.tip",
            type="mesh",
            mesh="mesh.cone",
            pos=tip_pos,
            material=object_material,
            size=None,
            mass=None,
            rgba=None,
            solimp=None,
            solref=None,
            contype=0,
            conaffinity=0,
        )

        body = Body(
            name=f"_{self.name}.{axis_name}",
            pos=body_pos,
            axisangle=axis_orientation,
        )
        body.add_child(_shaft_geom).add_child(_tip_geom)

        return body


class CoordinateSystemBody(Body):
    """Class to represent the coordinate system as a body in a MuJoCo model."""

    def __init__(
        self, name: str = "coordinate_system", pos: Position3d | None = None, yaw: Literal[0, 90, 180, 270] = 0
    ) -> None:
        """The constructor.

        Args:
            name: The name of the coordinate system body.
            pos: The position of the coordinate system body.
            yaw: The yaw angle of the coordinate system body.
        """

        super().__init__(
            name=name,
            pos=pos or (0, 0, 0),
        )
        coordinate_system = CoordinateSystem(pos_x=(0, 0, 0), pos_y=(0, 0, 0), pos_z=(0, 0, 0), yaw=yaw, name=name)
        for axis in coordinate_system.axes_as_body_objects():
            self.add_child(axis)
