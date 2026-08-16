from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.asset import Asset
from pet_physics.data_model.modeling.mjcf.option import Option
from pet_physics.data_model.modeling.mjcf.worldbody import Worldbody
from pet_physics.data_model.modeling.template_model import TemplateModel
from pet_physics.modeling.named_objects.coordinate_system import CoordinateSystem, CoordinateSystemAssets
from pet_physics.modeling.named_objects.floor import Floor, FloorMaterial, FloorTexture
from pet_physics.modeling.named_objects.light_diffuse import LightDiffuse
from pet_physics.modeling.named_objects.mesh_cone import MeshCone
from pet_physics.modeling.named_objects.texture_skybox import TextureSkybox


@dataclass
class PalletizingTemplateModel(TemplateModel):
    """Class represents a MuJoCo model that is used as template for palletizing simulations."""

    def __init__(
        self,
        name: str,
        asset: Asset | None = None,
        option: Option | None = None,
        worldbody: Worldbody | None = None,
    ) -> None:
        super().__init__(name=name, asset=asset, option=option, worldbody=worldbody)

    def _init_asset(self, asset: Asset) -> Asset:
        asset.add_child(TextureSkybox())
        asset.add_child(FloorMaterial()).add_child(FloorTexture()).add_child(MeshCone())
        for axis_material in CoordinateSystemAssets().materials:
            asset.add_child(axis_material)
        return asset

    def _init_option(self, option: Option) -> Option:
        return option

    def _init_worldbody(self, worldbody: Worldbody) -> Worldbody:
        worldbody.add_child(LightDiffuse()).add_child(Floor())
        for axis in CoordinateSystem().axes_as_body_objects():
            worldbody.add_child(axis)

        return worldbody

    @property
    def floor_body(self) -> Floor:
        for child in self.worldbody._children:
            if isinstance(child, Floor):
                return child
