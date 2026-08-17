"""Convenience functions for reading and writing data to and from files."""

from pathlib import Path


def get_output_dir_for_model_configuration(packing_plan_path: Path, write_into_home_subdir: bool = True) -> Path:
    """Returns the output directory for the model configuration corresponding to the given packing plan path.

    Args:
        packing_plan_path: The path to the bed-bpp packing plan JSON file.
        write_into_home_subdir: Whether to write the output into a subdirectory of the home directory.

    Returns:
        The output directory for the model configuration.
    """
    if write_into_home_subdir:
        return Path.home() / "pet_physics" / "model_configurations" / f"{packing_plan_path.stem}"
    else:
        return packing_plan_path.stem
