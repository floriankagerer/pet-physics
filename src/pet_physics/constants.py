"""Constants for the pet_physics package."""

BELOWNESS_THRESHOLD = 0.1
"""This value defines the distance below the top side of the carrier such that a body is not considered as touching
the floor and falling off a pallet, respectively."""
DEFAULT_SIM_END = 1200
"""The default value of the total simulation time in seconds."""
DEFAULT_TELEPORT_INTERVAL = 0.5
"""The default time between the teleports of two bodies in seconds."""
GRAVITY = 9.81
"""The gravity that is used in the simulation in m/s^2."""
THRESHOLD_NORM_LINEAR_ACCELERATION = 110
"""The limit for the norm of a body's **linear** acceleration such that a simulation run is defined to be valid."""
THRESHOLD_NORM_ANGULAR_ACCELERATION = 110
"""The limit for the norm of a body's **angular** acceleration such that a simulation run is defined
to be valid."""
UNIT_NORMAL_Z_AXIS = (0, 0, 1)
"""The unit normal that represents the direction of the z-axis."""
Z_COORDINATE_TOP_SIDE_OF_CARRIER = 0.0
"""The z-coordinate of the top side of the carrier."""
