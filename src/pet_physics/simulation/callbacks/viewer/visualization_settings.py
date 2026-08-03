"""Visualization settings for the MuJoCo simulation viewport.

Provides functions to toggle the visibility of contact points, contact forces, and the transparency of boxes in the
MuJoCo simulation viewport.
"""

import mujoco

from pet_physics.wrapper.mjt_vis_flag_wrapper import MjtVisFlag


def _toggle_visualization_flag(option: mujoco.MjvOption, flag: MjtVisFlag) -> None:
    """Toggles the value of the requested visualization flag.

    Args:
        option: The visualization options.
        flag: The visualization flag to toggle.
    """
    option.flags[flag] = not (option.flags[flag])


def visualize_contacts_and_forces(model: mujoco.MjModel, option: mujoco.MjvOption) -> None:
    """Sets flags in the visualization options such that the contacts of the bodies and the corresponding contact
    forces are displayed in the visualization.

    Args:
        model: The MuJoCo model.
        option: The visualization options.
    """
    mujoco.mjv_defaultOption(option)
    option.flags[MjtVisFlag.CONTACT_POINT] = False
    option.flags[MjtVisFlag.CONTACT_FORCE] = False
    option.flags[MjtVisFlag.TRANSPARENT] = False

    # tweak scales of contact visualization elements
    model.vis.scale.contactwidth = 0.1
    model.vis.scale.contactheight = 0.03
    model.vis.scale.forcewidth = 0.05
    model.vis.map.force = 0.3


def toggle_visibility_contact_points(option: mujoco.MjvOption) -> None:
    """Toggles the flag whether contact points are displayed.

    Args:
        option: The visualization options.
    """
    _toggle_visualization_flag(option=option, flag=MjtVisFlag.CONTACT_POINT)


def toggle_visibility_contact_forces(option: mujoco.MjvOption) -> None:
    """Toggles the flag whether contact forces are displayed.

    Args:
        option: The visualization options.
    """
    _toggle_visualization_flag(option=option, flag=MjtVisFlag.CONTACT_FORCE)


def toggle_transparency_boxes(option: mujoco.MjvOption) -> None:
    """Toggles the flag whether the transparency of boxes is applied.

    Args:
        option: The visualization options.
    """
    _toggle_visualization_flag(option=option, flag=MjtVisFlag.TRANSPARENT)
