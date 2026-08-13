"""Contains classes, functions, and utils for running a simulation with MuJoCo."""

from pathlib import Path

import mujoco

from pet_physics.modeling import get_path_and_placeholder_for_replacement


def _load_model(content: str) -> mujoco.MjModel:
    """Creates a MuJoCo model from the given content.

    Args:
        content: The content of the MuJoCo model.

    Returns:
        The model for the simulation.
    """
    # update the model content
    path_placeholder, path_replacement = get_path_and_placeholder_for_replacement()
    updated_model_content = content.replace(path_placeholder, path_replacement)

    return mujoco.MjModel.from_xml_string(updated_model_content)


def load_mujoco_model(model_file: Path) -> mujoco.MjModel:
    """Loads the MuJoCo model that is stored in the given file.

    Args:
        model_file: The file in that the model is stored.

    Returns:
        The model for the simulation.

    """
    with open(model_file) as file:
        model_content = file.read()

    return _load_model(model_content)


def load_mujoco_model_from_string(model_content: str) -> mujoco.MjModel:
    """Creates the MuJoCo model from the given string. If the string contains a placeholder, it is updated.

    Args:
        model_content: The content of the model file.

    Returns:
        The model for the simulation.
    """
    return _load_model(model_content)
