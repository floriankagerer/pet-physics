"""Data model for the MuJoCo body element with serialization support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NotRequired, TypedDict

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject
from pet_physics.data_model.modeling.mjcf.freejoint import Freejoint
from pet_physics.data_model.modeling.mjcf.geom import Geom
from pet_physics.data_model.serialization import from_dict, to_dict

CHILDREN_SERIALIZATION_KEY = "_type"


class BodyKwargs(TypedDict):
    """Keyword arguments for instantiating a `Body` object."""

    name: str
    pos: tuple[float, float, float]
    axisangle: NotRequired[tuple[int, int, int, int]]


@dataclass_json
@dataclass
class Body(BaseMJCFObject):
    """Class to represent a body with its associated properties and components.

    For details, see https://mujoco.readthedocs.io/en/stable/XMLreference.html#world-body-r
    """

    name: str
    pos: tuple[float, float, float]
    axisangle: tuple[int, int, int, int] | None = None

    @property
    def geom(self) -> Geom:
        """The `Geom` object of this `Body`."""
        for child in self._children:
            if isinstance(child, Geom):
                return child

        raise AttributeError(f"body '{self.name}' has no Geom child")

    @classmethod
    def custom_from_dict(cls, data: dict) -> Body:
        """Deserializes a `Body` from a dictionary, including its children.

        This method is assigned to `Body.from_dict` to override the
        `@dataclass_json`-generated version.

        Args:
            data (dict): The dictionary representation of a `Body`.

        Returns:
            Body: The deserialized `Body` instance.
        """
        body_obj: Body = cls(
            name=data.get("name"),
            pos=data.get("pos"),
            axisangle=data.get("axisangle"),
        )

        # deserialize the _children
        for child in data.get("_children"):
            child_type = child.pop(CHILDREN_SERIALIZATION_KEY)
            if child_type == "Freejoint":
                body_obj.add_child(from_dict(child, Freejoint))
            elif child_type == "Geom":
                body_obj.add_child(from_dict(child, Geom))
            else:
                msg = f"from_dict for type '{child_type}' is not implemented"
                raise NotImplementedError(msg)

        return body_obj

    def custom_to_dict(self) -> dict:
        """Serializes this `Body` to a dictionary, including its children.

        This method is assigned to `Body.to_dict` to override the
        `@dataclass_json`-generated version.

        Returns:
            dict: The dictionary representation of this `Body`.
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

    @property
    def has_freejoint(self) -> bool:
        """Indicates whether this body has a freejoint."""
        for child in self._children:
            if isinstance(child, Freejoint):
                return True

        return False


# Override the default from_dict
Body.from_dict = Body.custom_from_dict
# Override the default to_dict
Body.to_dict = Body.custom_to_dict


if __name__ == "__main__":
    # Creating the geom object for the body
    yellow_box_geom = Geom(
        name="yellow_box",
        type="box",
        size=(0.1, 0.1, 0.1),
        rgba=(1, 1, 0, 1),
        mass=1.0,
    )

    # Creating the body object
    top_box_body = Body(
        name="top_box",
        pos=(0, 0, 0.4),
    )

    # Adding the geometry to the body
    top_box_body.add_child(Freejoint())
    top_box_body.add_child(yellow_box_geom)

    # Now, `top_box_body` contains all the defined elements.
    print(top_box_body)
    print(top_box_body.to_xml_string())

    # de-/serialization
    serialized_geom = to_dict(yellow_box_geom)
    print(yellow_box_geom)
    print(serialized_geom)
    print(from_dict(serialized_geom, Geom), "\n\n")

    serialized_body = to_dict(top_box_body)
    print(top_box_body, "\n")
    print(serialized_body, "\n")
    print(from_dict(serialized_body, Body))
