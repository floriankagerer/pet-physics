"""Configuration for wiggle motion velocity components.

Stores and manages the x, y, and z velocity components used to apply wiggle motion to a simulated body.
"""

DEFAULT_VEL_X = 12
DEFAULT_VEL_Y = 0
DEFAULT_VEL_Z = 10


class WiggleConfig:
    """Velocity configuration for wiggle motion applied to a simulated body.

    Stores the velocity components for each axis and provides methods to increment or decrement each component.
    """

    def __init__(self) -> None:
        self._vel_x = DEFAULT_VEL_X
        self._vel_y = DEFAULT_VEL_Y
        self._vel_z = DEFAULT_VEL_Z

    @property
    def vel_x(self) -> int:
        """The current velocity in the x-direction."""
        return self._vel_x

    @property
    def vel_y(self) -> int:
        """The current velocity in the y-direction."""
        return self._vel_y

    @property
    def vel_z(self) -> int:
        """The current velocity in the z-direction."""
        return self._vel_z

    def increase_velocity_x(self) -> None:
        """Increments the x-axis velocity by 2 units."""
        self._vel_x += 2

    def decrease_velocity_x(self) -> None:
        """Decrements the x-axis velocity by 2 units."""
        self._vel_x -= 2

    def increase_velocity_y(self) -> None:
        """Increments the y-axis velocity by 2 units."""
        self._vel_y += 2

    def decrease_velocity_y(self) -> None:
        """Decrements the y-axis velocity by 2 units."""
        self._vel_y -= 2

    def increase_velocity_z(self) -> None:
        """Increments the z-axis velocity by 2 units."""
        self._vel_z += 2

    def decrease_velocity_z(self) -> None:
        """Decrements the z-axis velocity by 2 units."""
        self._vel_z -= 2
