"""Abstract base class for template MuJoCo models.

Defines `TemplateModel`, which pre-configures the asset, option, and worldbody elements shared by a family of
MuJoCo models so that subclasses only need to add the bodies specific to their use case.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pet_physics.data_model.modeling.mjcf.asset import Asset
from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.mujoco_model import MuJoCoModel
from pet_physics.data_model.modeling.mjcf.option import Option
from pet_physics.data_model.modeling.mjcf.worldbody import Worldbody
from pet_physics.data_model.modeling.template_model_config import TemplateModelConfig

_MSG_IMPLEMENT_METHOD_IN_CHILD_CLASS = "Method must be implemented in child class."


class TemplateModel(MuJoCoModel, ABC):
    """A MuJoCo model that pre-configures everything required to run a simulation for a given use case.

    Subclasses only need to supply the bodies specific to their use case; the asset, option, and worldbody
    elements shared across the use case are already set up.
    """

    def __init__(
        self,
        name: str,
        asset: Asset | None = None,
        option: Option | None = None,
        worldbody: Worldbody | None = None,
    ) -> None:
        """Sets up the shared asset, option, and worldbody elements for this template model.

        Args:
            name: The name of the MuJoCo model.
            asset: The asset to configure, or a default `Asset` if not provided.
            option: The option to configure, or a default `Option` if not provided.
            worldbody: The worldbody to configure, or a default `Worldbody` if not provided.
        """
        MuJoCoModel.__init__(self, model=name)

        # init asset
        if asset is None:
            asset = Asset()
        self._asset = self._init_asset(asset)
        self.add_child(self._asset)

        # init option
        if option is None:
            option = Option()
        self._option = self._init_option(option)
        self.add_child(self._option)

        # init worldbody
        if worldbody is None:
            worldbody = Worldbody()
        self._worldbody = self._init_worldbody(worldbody)
        self.add_child(self._worldbody)

    @abstractmethod
    def _init_asset(self, asset: Asset) -> Asset:
        """Configures the asset that is shared by all instances of this template model.

        Args:
            asset: The asset instance to configure.

        Returns:
            The configured asset.
        """
        raise NotImplementedError(_MSG_IMPLEMENT_METHOD_IN_CHILD_CLASS)

    @abstractmethod
    def _init_option(self, option: Option) -> Option:
        """Configures the option that is shared by all instances of this template model.

        Args:
            option: The option instance to configure.

        Returns:
            The configured option.
        """
        raise NotImplementedError(_MSG_IMPLEMENT_METHOD_IN_CHILD_CLASS)

    @abstractmethod
    def _init_worldbody(self, worldbody: Worldbody) -> Worldbody:
        """Configures the worldbody that is shared by all instances of this template model.

        Args:
            worldbody: The worldbody instance to configure.

        Returns:
            The configured worldbody.
        """
        raise NotImplementedError(_MSG_IMPLEMENT_METHOD_IN_CHILD_CLASS)

    @property
    def worldbody(self) -> Worldbody:
        """The `<worldbody .. />` elements in this model."""
        return self._worldbody

    @property
    @abstractmethod
    def floor_body(self) -> Body:
        """The body that represents the floor in the model."""
        raise NotImplementedError(_MSG_IMPLEMENT_METHOD_IN_CHILD_CLASS)

    @classmethod
    def from_config(cls, template_config: TemplateModelConfig) -> TemplateModel:
        """Creates a template model from a given configuration.

        Args:
            template_config: The configuration of the template.

        Returns:
            The created model, based on the template.
        """
        name = template_config.name
        option_kwargs = template_config.option_kwargs or {}

        option = Option(**option_kwargs)

        return cls(name=name, option=option)
