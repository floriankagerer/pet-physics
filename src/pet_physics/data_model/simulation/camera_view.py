"""Classes defining the view of the camera in the interactive viewer."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CameraView:
    """The position and orientation of the camera in the interactive viewer.

    Attributes:
        azimuth: Horizontal rotation of the camera around the lookat point, in degrees.
        elevation: Vertical rotation of the camera around the lookat point, in degrees.
        distance: Distance of the camera from the lookat point.
        lookat: 3D point in world coordinates that the camera is oriented towards.
    """

    azimuth: float
    elevation: float
    distance: float
    lookat: np.ndarray
