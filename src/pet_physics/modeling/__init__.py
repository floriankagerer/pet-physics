"""Classes, functions, and utils for creating MuJoCo simulation models."""

import os
from pathlib import Path

PATH_PLACEHOLDER = "$PATH_IS_REPLACED_WHEN_MODEL_IS_LOADED$"
"""This placeholder is replaced in the models when the model is loaded. If you want to load a file and use this
placeholder, the file path needs to start with `PATH_PLACEHOLDER/`, i.e., the parent of `modeling`."""


def get_path_and_placeholder_for_replacement() -> tuple[str, str]:
    """Returns the placeholder stored in models and its replacement path for loading.

    Returns:
        A tuple of (placeholder, path_replacement) where placeholder is the string stored in model files and
            path_replacement is the relative path used to correctly load those files.
    """
    current_working_directory = Path.cwd()
    abs_path_start_placeholder = Path(__file__).parents[1]

    path_replacement = os.path.relpath(abs_path_start_placeholder, current_working_directory)

    return PATH_PLACEHOLDER, path_replacement
