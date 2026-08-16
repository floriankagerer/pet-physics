"""Utility functions and classes for creating and manipulating MuJoCo model coordinates."""

import logging
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Literal

import mujoco
import numpy as np

from pet_physics.type_alias_definition import Position3d, Size3d

DIVISOR_MAPPING = {"mm": 1000, "cm": 100, "dm": 10, "m": 1}
"""The divisor such that we get the results in meters."""
DEFAULT_WEIGHT_G = 1000.0
"""The default weight of a box in gramms. This value is used whenever no property is given or if the weight is `0.0`."""
ENCODING_MAPPER = {"#": "\\#", "&": "AND", '"': "\\u0022"}
"""The keys are problematic characters and the values the corresponding replacements."""

logger = logging.getLogger(__name__)


def custom_name_encode(body_name: str) -> str:
    """Encodes a body name by replacing characters that are problematic in MuJoCo model files.

    For the list of replaced characters, see `ENCODING_MAPPER`.

    Args:
        body_name: The body name to encode.

    Returns:
        The body name with problematic characters replaced.
    """
    encoded_string = body_name
    for old_char, new_char in ENCODING_MAPPER.items():
        encoded_string = encoded_string.replace(old_char, new_char)
    return encoded_string


def bankers_rounding(value: float, ndigits: int) -> float:
    """Rounds a value using banker's rounding (round half to even).

    For details, see https://en.wikipedia.org/wiki/Rounding#Rounding_half_to_even.

    Args:
        value: The value to round.
        ndigits: The number of decimal digits to keep.

    Returns:
        The rounded value.
    """
    return round(value, ndigits)


def round_half_up(value: float, ndigits: int) -> float:
    """Rounds a value using conventional rounding (round half up).

    Args:
        value: The value to round.
        ndigits: The number of decimal digits to keep.

    Returns:
        The rounded value.

    Raises:
        ValueError: If ndigits is less than 1.
    """
    if ndigits < 1:
        raise ValueError("ndigits must be >= 1")

    number = Decimal(str(value))

    precision = "0." + "0" * (ndigits - 1) + "1"
    rounded_value = number.quantize(Decimal(precision), rounding=ROUND_HALF_UP)

    return float(rounded_value)


def get_body_and_geom_name(counter: int | str, body_identifier: str) -> tuple[str, str]:
    """Creates the body and geom names for a MuJoCo model element.

    Args:
        counter: A counter or string prefix to ensure unique names.
        body_identifier: The body identifier, e.g., product and SKU name.

    Returns:
        A tuple of (body_name, geom_name).
    """
    body_name = f"{counter}_{body_identifier}"
    body_name = custom_name_encode(body_name)
    geom_name = body_name + ".box"

    return body_name, geom_name


class MJCFUtils:
    """Static utility methods for converting coordinates and properties to MuJoCo format."""

    @staticmethod
    def convert_to_mjcf_coordinates(
        flb: Position3d,
        size: Size3d,
        size_reduction: float | int = 0.0,
        unit: Literal["mm", "cm", "dm", "m"] = "mm",
        ndigits: int = 6,
    ) -> tuple[Size3d, Position3d]:
        """Converts the FLB coordinates and the size of an object such that it is correctly used in MuJoCo.

        Args:
            flb: The flb coordinates of the object.
            size: The size of the object.
            size_reduction: Defines the size reduction of the object.
            unit: The unit of `flb`, `size`, and `size_reduction`.
            ndigits: The number of digits of the returned size and position.

        Returns:
            The size of the object in MJCF coordinates and the position of the object in MJCF coordinates.
        """
        mjcf_size = [(s - size_reduction) / 2 for s in size]
        mjcf_pos = [c + mjcf_s for c, mjcf_s in zip(flb, mjcf_size)]

        divisor = DIVISOR_MAPPING[unit]
        si_unit_size = [round_half_up(val / divisor, ndigits) for val in mjcf_size]
        si_unit_pos = [round_half_up(val / divisor, ndigits) for val in mjcf_pos]

        return tuple(si_unit_size), tuple(si_unit_pos)

    @staticmethod
    def convert_to_mjcf_pos(
        flb: Position3d, unit: Literal["mm", "cm", "dm", "m"] = "mm", ndigits: int = 6
    ) -> Position3d:
        """Converts the FLB coordinates of an object to MJCF coordinates.

        Args:
            flb: The flb coordinates of the object.
            unit: The unit of `flb`.
            ndigits: The number of digits of the returned position.

        Returns:
            The position of the object in MJCF coordinates.
        """
        divisor = DIVISOR_MAPPING[unit]
        si_unit_pos = [round_half_up(val / divisor, ndigits) for val in flb]
        return tuple(si_unit_pos)

    @staticmethod
    def convert_gramms_to_kg(mass_in_gramm: int | float) -> float:
        """Converts a mass value from grammes to kilograms.

        Args:
            mass_in_gramm: The mass in grammes.

        Returns:
            The mass in kilograms, rounded to 3 decimal places.
        """
        if np.isclose(mass_in_gramm, 0.0):
            msg = "mass is too close to 0.0 -> use default weight instead"
            logger.warning(msg)
            mass_in_gramm = DEFAULT_WEIGHT_G

        mass_in_kg = round(mass_in_gramm / 1000, 3)
        return mass_in_kg

    @staticmethod
    def export_model_to_mjcf_file(file_path: Path, model: mujoco.MjModel) -> None:
        """Saves a MuJoCo model as an MJCF file.

        Args:
            file_path: The output file path.
            model: The model to export.
        """
        mujoco.mj_saveLastXML(file_path.as_posix(), model)
        logger.info(f"wrote mujoco model to '{file_path.as_posix()}'")

    @staticmethod
    def tuple_to_mjcf_string(props_tuple: tuple[float, float, float]) -> str:
        """Converts a tuple of floats to a space-separated string for MuJoCo XML.

        Args:
            props_tuple: A tuple of float values.

        Returns:
            The values joined by spaces.
        """
        return " ".join(map(str, props_tuple))
