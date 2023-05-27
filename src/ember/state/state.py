from copy import copy
from ember.material import Material
from typing import Sequence, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..ui.view_layer import ViewLayer
    from ..ui.base.element import Element

from ..style.load_material import load_material


def load_state(
    state: Optional["State"],
    material: Optional[Material],
    fallback_state: Optional["State"],
) -> "State":
    """
    Used inside of Styles for material loading. For interal use only.
    """
    if isinstance(state, State):
        if material:
            state.material = material
        return state
    elif fallback_state is not None:
        return State(
            load_material(material, fallback_state.material),
            element_offset=fallback_state.element_offset,
        )
    else:
        return State(load_material(material, None))


def load_background(
    element: Union["Element", "ViewLayer"], background: Union["State", Material, None]
) -> Optional["State"]:
    """
    Used by Elements to load backgrounds into states.
    """
    if isinstance(background, State):
        return background
    elif isinstance(background, Material):
        state = element._style.default_state.copy()
        state.material = background
        return state
    elif background is None:
        return None
    else:
        raise ValueError(
            f"Background must be of type State, Material or None - not {type(background).__name__}."
        )


class State:
    __slots__ = ("material", "element_offset", "element_alpha")

    def __init__(
        self,
        material: Optional[Material] = None,
        element_offset: Sequence[int] = (0, 0),
        element_alpha: int = 255,
    ):
        self.material: Optional[Material] = material
        self.element_offset: Sequence[int] = element_offset
        self.element_alpha: int = element_alpha

    def copy(self) -> "State":
        return copy(self)


StateType = Union[State, Material, None]
