from typing import Optional, Literal, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ember.ui.base.container import Container

from .. import common as _c
from .style import Style, MaterialType

from ..transition.transition import Transition
from ..material.blank import Blank

from ..state.state import State, load_state
from . import defaults


def default_state_func(container: "Container") -> State:
    if container.background:
        return container.background
    elif container.layer.element_focused is container:
        return container._style.focus_state
    elif (
        container.layer.element_focused is not None
        and container in container.layer.element_focused.get_parent_tree()
    ):
        return container._style.focus_child_state
    else:
        return container._style.default_state


class ContainerStyle(Style):
    def __init__(
        self,
        default_state: MaterialType = None,
        focus_state: MaterialType = None,
        focus_child_state: MaterialType = None,
        default_material: MaterialType = None,
        focus_material: MaterialType = None,
        focus_child_material: MaterialType = None,
        spacing: Optional[int] = None,
        min_spacing: int = 6,
        focus_self: bool = False,
        focus_on_entry: Literal["closest", "first"] = "closest",
        align_elements_v: Literal["left", "center", "right"] = "center",
        align_elements_h: Literal["top", "center", "bottom"] = "center",
        material_transition: Optional[Transition] = None,
        state_func: Optional[Callable[["Container"], "State"]] = None,
    ):
        self.default_state: State = load_state(default_state, default_material, None)
        """
        The default State.
        """
        self.focus_state: State = load_state(
            focus_state, focus_material, self.default_state
        )
        """
        Shown when the Container is focused. Uses the default state if no state is specified.
        """
        self.focus_child_state: State = load_state(
            focus_child_state, focus_child_material, self.focus_state
        )
        """
        Shown when a child of the Container is focused. Uses the focus state if no state is specified.
        """

        self.spacing: Optional[int] = spacing
        """
        The spacing between the elements. If set to None, the elements will 
        be spaced evenly the fill the whole Container. 
        """

        self.min_spacing: int = min_spacing
        """
        The minimum spacing between the elements. Only effective if the 'spacing' attribute is None.
        """

        self.focus_self: bool = focus_self
        """
        Modifies how the Container behaves with keyboard / controller navigation. If set to True, the Container itself 
        is focusable. If you press enter when the Container is focused, the first child of the Container is focused.
        """

        self.focus_on_entry: Literal["closest", "first"] = focus_on_entry

        self.align_elements_v: Literal["left", "center", "right"] = align_elements_v
        """
        The alignments of elements in vertical containers.
        """
        self.align_elements_h: Literal["top", "center", "bottom"] = align_elements_h
        """
        The alignments of elements in horizontal containers.
        """

        self.material_transition: Optional[Transition] = material_transition
        """
        The Transition to use when changing States.
        """

        self.state_func: Callable[["Container"], "State"] = (
            state_func if state_func is not None else default_state_func
        )
        """
        The function that determines which state is active. Can be replaced for more control over the Container's states.
        """

    def set_as_default(self) -> "ContainerStyle":
        defaults.container = self
        return self
