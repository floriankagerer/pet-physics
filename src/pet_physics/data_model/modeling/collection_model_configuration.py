"""Data model for a collection of model configurations belonging to the same packing plan.

Defines `CollectionModelConfiguration`, which groups the `ModelConfiguration` objects for bins that logically
belong together and can serialize them all to a single YAML file.
"""

import logging
from collections.abc import Generator
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from pet_physics.data_model.model_configuration import ModelConfiguration

logger = logging.getLogger(__name__)


@dataclass
class CollectionModelConfiguration:
    """Model configurations for multiple bins that logically belong together.

    For example, this groups configurations for bins that belong to the same packing plan.

    Attributes:
        configurations: The model configurations contained in this collection.
    """

    configurations: list[ModelConfiguration] | None = field(default_factory=list)

    def add_config(self, config: ModelConfiguration) -> None:
        """Adds the given configuration to this collection."""
        self.configurations.append(config)

    def items(self) -> Generator[tuple[str, ModelConfiguration], None, None]:
        """Iterates over the configurations in this collection paired with their model names.

        Yields:
            A tuple (model_name, config) for each configuration in this collection.
        """
        for config in self.configurations:
            yield config.model_name, config

    def write_to_file(self, output_path: Path) -> None:
        """Writes the model configurations to the specified file path.

        Args:
            output_path: The file to which the model configurations are written.
        """
        content = {key: config.to_yaml() for key, config in self.items()}
        with open(output_path, "w") as file:
            yaml.dump(content, file, sort_keys=False)
        logger.info(f"wrote model configurations to '{output_path}'")
