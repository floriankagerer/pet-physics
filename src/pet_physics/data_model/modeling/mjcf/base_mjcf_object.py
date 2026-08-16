"""Base class for all MuJoCo model data objects with XML serialization support."""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from abc import ABC
from collections.abc import Generator
from dataclasses import dataclass, field, fields

from pet_physics.utils.mjcf_utils import MJCFUtils


@dataclass
class BaseMJCFObject(ABC):
    """The base class for objects that occur in a MuJoCo modeling file."""

    _children: list[BaseMJCFObject] = field(default_factory=list, init=False)
    """All objects that are children of this object, e.g., `Geom` is a child of `Body`."""

    def to_xml(self, tag: str | None = None) -> ET.Element:
        """Converts this instance to an XML element.

        Args:
            tag (Optional[str]): The XML tag to use. If None, the tag is derived
                from the name of the class that directly inherits from
                `BaseMJCFObject`.

        Returns:
            ET.Element: The XML element representing this object.
        """
        # derive the xml tag
        if tag is None:
            xml_tag = self.serialization_key.lower()
        else:
            xml_tag = tag.lower()

        xml_element = ET.Element(xml_tag)

        for attr_name, attr_val in self.get_assigned_attributes():
            if isinstance(attr_val, (tuple, list)):
                xml_element.set(attr_name, MJCFUtils.tuple_to_mjcf_string(attr_val))
            else:
                xml_element.set(attr_name, str(attr_val))

        for child in self._children:
            xml_element.append(child.to_xml())

        return xml_element

    def add_child(self, child: BaseMJCFObject) -> BaseMJCFObject:
        """Adds a child object to this element and returns self for chaining.

        Args:
            child (BaseMJCFObject): The child object to add.

        Returns:
            BaseMJCFObject: This instance.
        """
        self._children.append(child)
        return self

    def get_assigned_attributes(
        self,
    ) -> Generator[tuple[str, float | int | str], None, None]:
        """Yields all non-None, non-empty attributes, excluding `_children`.

        Yields:
            tuple[str, float | int | str]: A tuple of (name, value) for each
                assigned attribute.
        """
        for _field in fields(self):
            name = _field.name
            if name == "_children":
                continue
            value = getattr(self, name)

            if (value is not None) and (value != []):
                yield name, value

    def to_xml_string(self) -> str:
        """Converts this instance to an XML string.

        Returns:
            str: The XML string representation of this object.
        """
        return html.unescape(ET.tostring(self.to_xml(), encoding="unicode"))

    @property
    def serialization_key(self) -> str:
        """The name of the class that directly inherits from `BaseMJCFObject`.

        For example, `Geom(BaseMJCFObject)` has key `"Geom"` and
        `CardboardGeom(Geom)` also has key `"Geom"`.
        """
        ancestors = self.__class__.__mro__
        direct_descendant_of_base_mjcf = ancestors[ancestors.index(BaseMJCFObject) - 1]
        return direct_descendant_of_base_mjcf.__name__
