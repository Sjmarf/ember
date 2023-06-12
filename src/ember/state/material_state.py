import pygame
import abc
from .state import State
from typing import Optional, TYPE_CHECKING
from ember.utility.load_material import load_material

from .. import common as _c

if TYPE_CHECKING:
    from .state_controller import StateController
    from ..material.material import Material
    from ..transition.transition import Transition


class MaterialState(State, abc.ABC):
    @abc.abstractmethod
    def get_material(self, index: int) -> Optional["Material"]:
        pass


class SingleMaterialState(MaterialState):
    def __init__(self, material: Optional["Material"] = None):
        self.material: Optional["Material"] = material

    @classmethod
    def _load(
        cls,
        state: Optional["SingleMaterialState"],
        material: Optional["Material"],
        fallback_state: Optional["SingleMaterialState"] = None,
    ):
        """
        Used inside of Styles for material loading. For interal use only.
        """
        if isinstance(state, State):
            if material is not None:
                state.material = material
            return state
        elif fallback_state is not None:
            new_state = fallback_state.copy()
            new_state.material = load_material(material, fallback_state.material)
            return new_state
        else:
            return cls(material=load_material(material, None))

    def get_material(self, index: int) -> Optional["Material"]:
        return self.material


class BaseHandleMaterialState(MaterialState):
    def __init__(
        self,
        base_material: Optional["Material"] = None,
        handle_material: Optional["Material"] = None,
    ):
        self.base_material: Optional["Material"] = base_material
        self.handle_material: Optional["Material"] = handle_material

    @classmethod
    def _load(
        cls,
        state: Optional["BaseHandleMaterialState"],
        base_material: Optional["Material"],
        handle_material: Optional["Material"],
        fallback_state: Optional["BaseHandleMaterialState"] = None,
    ):
        """
        Used inside of Styles for material loading. For interal use only.
        """
        if isinstance(state, State):
            if base_material is not None:
                state.base_material = base_material
            if handle_material is not None:
                state.handle_material = handle_material
            return state
        elif fallback_state is not None:
            new_state = fallback_state.copy()
            new_state.base_material = load_material(
                base_material, fallback_state.base_material
            )
            new_state.handle_material = load_material(
                handle_material, fallback_state.handle_material
            )
            return new_state
        else:
            return cls(
                base_material=load_material(base_material, None),
                handle_material=load_material(handle_material, None),
            )

    def get_material(self, index: int) -> Optional["Material"]:
        return self.base_material if index == 0 else self.handle_material
