"""Overlay management for the MuJoCo simulation viewport.

Provides `OverlayUpdater` for rendering simulation status text and key bindings as an on-screen overlay, and
`GridPosition` for specifying the anchor position of each overlay entry.
"""

from enum import Enum

import mujoco


class GridPosition(Enum):
    """Available anchor positions for overlay text in the MuJoCo viewport.

    Attributes:
        TOP_LEFT: Top left position.
        TOP_RIGHT: Top right position.
        BOTTOM_LEFT: Bottom left position.
        BOTTOM_RIGHT: Bottom right position.
    """

    TOP_LEFT = mujoco.mjtGridPos.mjGRID_TOPLEFT
    TOP_RIGHT = mujoco.mjtGridPos.mjGRID_TOPRIGHT
    BOTTOM_LEFT = mujoco.mjtGridPos.mjGRID_BOTTOMLEFT
    BOTTOM_RIGHT = mujoco.mjtGridPos.mjGRID_BOTTOMRIGHT


class OverlayUpdater:
    """Manager for the on-screen overlay in the MuJoCo simulation viewport.

    The overlay displays various information and controls related to the simulation.
    """

    def __init__(self) -> None:
        self._overlay = {}

    @property
    def overlay(self) -> dict:
        """The entries of the overlay."""
        return self._overlay

    def clear_overlay(self) -> None:
        """Resets the overlay to an empty state."""
        self._overlay = {}

    def _add(self, overlay: dict, grid_position: GridPosition, text1: str, text2: str) -> None:
        """Appends a labeled text entry at the specified grid position.

        Args:
            overlay: The dict that holds the overlay items.
            grid_position: The grid position to which the text entry is anchored.
            text1: The label text shown in the left column.
            text2: The value or command text shown in the right column.
        """
        if grid_position.value not in overlay:
            overlay[grid_position.value] = ["", ""]

        overlay[grid_position.value][0] += text1 + "\n"
        overlay[grid_position.value][1] += text2 + "\n"

    def _create_overlay(
        self,
        data: mujoco.MjData,
        callback_related: dict,
        simulation_status: dict,
    ) -> dict:
        """Builds the overlay text entries for the current simulation frame.

        Args:
            data: The current simulation data object.
            callback_related: A mapping of callback names to their handler objects.
            simulation_status: Contains information about the simulation status, e.g., whether all bodies
                are teleported.

        Returns:
            A dict mapping `GridPosition` values to two-element string lists, where the first element is the label
                column and the second is the value column.
        """
        overlay = {}
        self._add(overlay, GridPosition.BOTTOM_LEFT, "Quit", "q")
        self._add(overlay, GridPosition.BOTTOM_LEFT, "Restart", "r")
        self._add(overlay, GridPosition.BOTTOM_LEFT, "Start", "s")
        self._add(overlay, GridPosition.BOTTOM_LEFT, "Time", "%.2f" % data.time)
        self._add(overlay, GridPosition.BOTTOM_RIGHT, "Toggle transparency", "t")
        self._add(overlay, GridPosition.BOTTOM_RIGHT, "Toggle contact forces", "c")

        wiggle_callback = callback_related.get("wiggle", None)
        if wiggle_callback:
            self._add(
                overlay,
                GridPosition.TOP_LEFT,
                "vel x ('1' + up/down)",
                "%.2f" % wiggle_callback.vel_x,
            )
            self._add(
                overlay,
                GridPosition.TOP_LEFT,
                "vel y ('2' + up/down)",
                "%.2f" % wiggle_callback.vel_y,
            )
            self._add(
                overlay,
                GridPosition.TOP_LEFT,
                "vel z ('3' + up/down)",
                "%.2f" % wiggle_callback.vel_z,
            )

        if simulation_status.get("all_items_palletized", None):
            self._add(
                overlay,
                GridPosition.TOP_RIGHT,
                "All items palletized",
                "",
            )

        return overlay

    def _apply_overlay(self, overlay: dict, viewport: mujoco.MjrRect, context: mujoco.MjrContext) -> None:
        """Draws all overlay text entries onto the given viewport."""
        for gridpos, [string_1, string_2] in overlay.items():
            mujoco.mjr_overlay(
                mujoco.mjtFontScale.mjFONTSCALE_150,
                gridpos,
                viewport,
                string_1,
                string_2,
                context,
            )

    def update_overlay(
        self,
        model: mujoco.MjModel,
        data: mujoco.MjData,
        viewport: mujoco.MjrRect,
        context: mujoco.MjrContext,
        callback_related: dict,
        simulation_status: dict,
    ) -> None:
        """Renders the current simulation state as overlay text on the viewport.

        Args:
            model: The MuJoCo model object.
            data: The current simulation data object.
            viewport: The rectangular region of the viewport to render into.
            context: The MuJoCo rendering context.
            callback_related: A mapping of callback names to their handler objects.
            simulation_status: Contains information about the simulation status, e.g., whether all bodies
                are teleported.
        """
        overlay = self._create_overlay(data, callback_related, simulation_status)
        self._apply_overlay(overlay, viewport, context)
