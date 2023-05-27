from typing import Optional, TYPE_CHECKING, Callable

from .. import common as _c

from .style import Style, MaterialType
from ..state.state import State, load_state

if TYPE_CHECKING:
    from ..transition.transition import Transition
    from ..ui.view_layer import ViewLayer

from ..material.blank import Blank
from . import defaults


def default_state_func(view_layer: "ViewLayer") -> State:
    if view_layer.background:
        return view_layer.background
    else:
        return view_layer._style.default_state


class ViewStyle(Style):
    def __init__(
        self,
        default_state: Optional[State] = None,
        default_material: MaterialType = None,
        transition: Optional["Transition"] = None,
        transition_in: Optional["Transition"] = None,
        transition_out: Optional["Transition"] = None,
        state_func: Optional[Callable[["ViewLayer"], "State"]] = None,
    ):
        self.default_state: State = load_state(default_state, default_material, None)
        """
        The default State of the ViewLayer.
        """

        self.transition_in: Optional["Transition"] = (
            transition_in if transition_in else transition
        )
        """
        The Transition to use when the ViewLayer is transitioning in.
        """
        self.transition_out: Optional["Transition"] = (
            transition_out if transition_out else transition
        )
        """
        The Transition to use when the ViewLayer is transitioning out.
        """

        self.state_func: Callable[["ViewLayer"], "State"] = (
            state_func if state_func is not None else default_state_func
        )
        """
        The function that determines which state is active.
        Can be replaced for more control over the ViewLayer's states.
        """

    def set_as_default(self) -> "ViewStyle":
        defaults.view = self
        return self
