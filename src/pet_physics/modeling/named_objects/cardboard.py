from dataclasses import dataclass

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.geom import Geom

CARDBOARD_FRICTION = (0.5, 0.005, 0.0001)
"""The value of the sliding friction, torsional friction, and the rolling friction for a cardboard geometry."""


@dataclass_json
@dataclass
class CardboardGeom(Geom):
    """Represents a cardboard geometry object, i.e., a geom object with the friction value of a cardboard.

    The value of the friction is taken from
    https://wiki.unece.org/display/TransportSustainableCTUCode/Appendix+2.%09Friction+factors
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            **kwargs,
            friction=CARDBOARD_FRICTION,
        )
