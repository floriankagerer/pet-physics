"""Data model for the MuJoCo flexcomp element representing deformable bodies.

See https://github.com/google-deepmind/mujoco/blob/d21f624264d938cd722d761ad8b695c0383a29f6/model/flex/gripper.xml#L28
and https://github.com/google-deepmind/mujoco/blob/d21f624264d938cd722d761ad8b695c0383a29f6/model/composite/softbox.xml#L27
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject
from pet_physics.data_model.modeling.mjcf.contact import Contact
from pet_physics.data_model.modeling.mjcf.edge import Edge
from pet_physics.data_model.serialization import from_dict, to_dict

CHILDREN_SERIALIZATION_KEY = "_type"
"""Serialization key that is required for a correct deserialization."""


class FlexcompKwargs(TypedDict):
    """Keyword arguments for instantiating a `Flexcomp` object."""

    name: str
    pos: tuple[float, float, float]
    mass: float
    count: tuple[int, int, int]
    spacing: tuple[float, float, float]
    dim: NotRequired[int]
    type: NotRequired[Literal["grid", "box"]]
    rigid: NotRequired[Literal["false"]]
    rgba: NotRequired[tuple[float, float, float, float]]
    radius: NotRequired[float]


@dataclass_json
@dataclass
class Flexcomp(BaseMJCFObject):
    """Deformable body element using MuJoCo's `flexcomp` macro.

    For details, see https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-flexcomp
    """

    name: str
    pos: tuple[float, float, float]
    mass: float
    count: tuple[int, int, int]
    spacing: tuple[float, float, float]
    dim: int = 3
    type: Literal["grid", "box"] = "grid"
    rigid: Literal["false"] = "false"
    rgba: tuple[float, float, float, float] = (0.9, 0.9, 0.9, 1.0)
    radius: float = 0.000001

    @classmethod
    def custom_from_dict(cls, data: dict) -> Flexcomp:
        """Deserializes a `Flexcomp` from a dictionary, including its children.

        This method is assigned to `Flexcomp.from_dict` to override the
        `@dataclass_json`-generated version.

        Args:
            data (dict): The dictionary representation of a `Flexcomp`.

        Returns:
            Flexcomp: The deserialized `Flexcomp` instance.
        """
        body_obj: Flexcomp = cls(
            name=data.get("name"),
            pos=data.get("pos"),
            mass=data.get("mass"),
            dim=data.get("dim"),
            type=data.get("type"),
            rigid=data.get("rigid"),
            count=data.get("count"),
            spacing=data.get("spacing"),
            rgba=data.get("rgba"),
            radius=data.get("radius"),
        )

        # deserialize the _children
        for child in data.get("_children"):
            child_type = child.pop(CHILDREN_SERIALIZATION_KEY)
            if child_type == "Edge":
                body_obj.add_child(from_dict(child, Edge))
            elif child_type == "Contact":
                body_obj.add_child(from_dict(child, Contact))
            else:
                msg = f"from_dict for type '{child_type}' is not implemented"
                raise NotImplementedError(msg)

        return body_obj

    def custom_to_dict(self) -> dict:
        """Serializes this `Flexcomp` to a dictionary, including its children.

        This method is assigned to `Flexcomp.to_dict` to override the
        `@dataclass_json`-generated version.

        Returns:
            dict: The dictionary representation of this `Flexcomp`.
        """
        self_as_dict = {}

        for field_name in self.__dataclass_fields__:
            value: list[BaseMJCFObject] = getattr(self, field_name)

            if field_name == "_children":
                children_as_dict = []
                for child in value:
                    child_as_dict = to_dict(child)
                    child_as_dict[CHILDREN_SERIALIZATION_KEY] = child.serialization_key
                    children_as_dict.append(child_as_dict)

                self_as_dict[field_name] = children_as_dict
            else:
                if isinstance(value, tuple):
                    value = list(value)
                self_as_dict[field_name] = value

        return self_as_dict


# Override the default from_dict
Flexcomp.from_dict = Flexcomp.custom_from_dict
# Override the default to_dict
Flexcomp.to_dict = Flexcomp.custom_to_dict
