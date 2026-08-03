"""Tests for viewer visualization setting toggles."""

import mujoco
import pytest

from pet_physics.simulation.callbacks.viewer.visualization_settings import (
    toggle_transparency_boxes,
    toggle_visibility_contact_forces,
    toggle_visibility_contact_points,
    visualize_contacts_and_forces,
)
from pet_physics.wrapper.mjt_vis_flag_wrapper import MjtVisFlag

_MODEL_XML = """
<mujoco>
  <worldbody>
    <geom type="plane" size="1 1 0.1" />
  </worldbody>
</mujoco>
"""


@pytest.fixture
def model() -> mujoco.MjModel:
    """A minimal MuJoCo model used to exercise visualization scale settings."""
    return mujoco.MjModel.from_xml_string(_MODEL_XML)


@pytest.fixture
def option() -> mujoco.MjvOption:
    """A default `mujoco.MjvOption` instance."""
    return mujoco.MjvOption()


@pytest.mark.parametrize(
    ("toggle_function", "flag"),
    [
        (toggle_visibility_contact_points, MjtVisFlag.CONTACT_POINT),
        (toggle_visibility_contact_forces, MjtVisFlag.CONTACT_FORCE),
        (toggle_transparency_boxes, MjtVisFlag.TRANSPARENT),
    ],
)
def test_toggle_flips_only_the_targeted_flag(toggle_function, flag: MjtVisFlag, option: mujoco.MjvOption) -> None:
    """Toggling a visualization flag should flip only that flag, leaving the others untouched."""
    other_flags = [f for f in MjtVisFlag if f != flag]
    other_flags_before = [option.flags[f] for f in other_flags]
    flag_before = option.flags[flag]

    toggle_function(option)

    assert option.flags[flag] == (not flag_before)
    assert [option.flags[f] for f in other_flags] == other_flags_before


@pytest.mark.parametrize(
    "toggle_function",
    [toggle_visibility_contact_points, toggle_visibility_contact_forces, toggle_transparency_boxes],
)
def test_toggle_twice_restores_original_value(toggle_function, option: mujoco.MjvOption) -> None:
    """Toggling a visualization flag twice should restore its original value."""
    flag = {
        toggle_visibility_contact_points: MjtVisFlag.CONTACT_POINT,
        toggle_visibility_contact_forces: MjtVisFlag.CONTACT_FORCE,
        toggle_transparency_boxes: MjtVisFlag.TRANSPARENT,
    }[toggle_function]
    initial_value = option.flags[flag]

    toggle_function(option)
    toggle_function(option)

    assert option.flags[flag] == initial_value


def test_visualize_contacts_and_forces_disables_flags_and_sets_scales(
    model: mujoco.MjModel, option: mujoco.MjvOption
) -> None:
    """Should reset contact/transparency flags to `False` and configure the contact visualization scales."""
    option.flags[MjtVisFlag.CONTACT_POINT] = True
    option.flags[MjtVisFlag.CONTACT_FORCE] = True
    option.flags[MjtVisFlag.TRANSPARENT] = True

    visualize_contacts_and_forces(model, option)

    assert not option.flags[MjtVisFlag.CONTACT_POINT]
    assert not option.flags[MjtVisFlag.CONTACT_FORCE]
    assert not option.flags[MjtVisFlag.TRANSPARENT]
    assert model.vis.scale.contactwidth == pytest.approx(0.1)
    assert model.vis.scale.contactheight == pytest.approx(0.03)
    assert model.vis.scale.forcewidth == pytest.approx(0.05)
    assert model.vis.map.force == pytest.approx(0.3)
