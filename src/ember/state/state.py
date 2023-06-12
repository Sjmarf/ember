from copy import copy
from ember.material import Material
from typing import Type, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..ui.view_layer import ViewLayer
    from ..ui.base.element import Element

class State:
    def copy(self) -> "State":
        return copy(self)


StateType = Union[State, Material, None]


def load_background(
    element: Union["Element", "ViewLayer"], material: Union["State", Material, None]
) -> Optional["State"]:
    """
    Used by Elements to load backgrounds into states.
    """
    if isinstance(material, State):
        return material
    elif isinstance(material, Material):
        state = element._style.default_state.copy()
        state.material = material
        return state
    elif material is None:
        return None
    else:
        raise ValueError(
            f"Background must be of type State, Material or None - not {type(material).__name__}."
        )
