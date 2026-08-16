"""Data model for the top-level MuJoCo model element with file output support."""

from dataclasses import dataclass
from pathlib import Path
from xml.etree.ElementTree import Element

import structlog

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject

logger = structlog.get_logger(__name__)


@dataclass
class MuJoCoModel(BaseMJCFObject):
    """Represents the top-level `<mujoco>` element of a MuJoCo model file.

    Attributes:
        model: The name of the model.
    """

    model: str

    def to_xml(self) -> Element:
        """Converts this model to an XML element with tag `mujoco`.

        Returns:
            The XML element representing the model.
        """
        return super().to_xml(tag="mujoco")

    def write_to_file(self, output_path: Path) -> None:
        """Writes the model XML to the specified file path.

        Args:
            output_path: The file path to write the model to.
        """
        with open(output_path, "w") as file:
            file.write(self.to_xml_string())
        logger.info(f"wrote model to '{output_path}'")
