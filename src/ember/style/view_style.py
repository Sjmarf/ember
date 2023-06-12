from typing import Optional, TYPE_CHECKING, Callable

from .. import common as _c
from ..common import MaterialType

from .style import Style

if TYPE_CHECKING:
    from ..transition.transition import Transition

from ..state.state import State
from ..state.background_state import BackgroundState

from ..size import SizeType, SequenceSizeType, Size
from ..ui.view_layer import ViewLayer


class ViewStyle(Style):
    _ELEMENT = ViewLayer

    @staticmethod
    def default_state_func(view_layer: "ViewLayer") -> "BackgroundState":
        if view_layer.material:
            return view_layer.material
        else:
            return view_layer._style.default_state

    def __init__(
        self,
        size: SequenceSizeType = (300, 80),
        width: SizeType = None,
        height: SizeType = None,
        default_state: Optional["BackgroundState"] = None,
        default_material: Optional[MaterialType] = None,
        listen_for_exit: bool = False,
        transition: Optional["Transition"] = None,
        transition_in: Optional["Transition"] = None,
        transition_out: Optional["Transition"] = None,
        auto_transition_in: bool = False,
        material_transition: Optional["Transition"] = None,
        state_func: Callable[["ViewLayer"], "BackgroundState"] = default_state_func,
    ):
        self.size: tuple[Size, Size] = self.load_size(size, width, height)
        """
        The size of the Element if no size is specified in the Element constructor.
        """

        self.default_state: "BackgroundState" = BackgroundState._load(
            default_state, default_material
        )
        """
        The default State of the ViewLayer.
        """

        self.listen_for_exit: bool = listen_for_exit
        """
        If True, the ViewLayer triggers its exit transition when the Escape key 
        (or the equivalent controller button) is pressed. 
        You can trigger the exit transition yourself by calling ViewLayer.exit() if you prefer.
        """

        self.auto_transition_in: bool = auto_transition_in
        """
        If True, :py:meth:`ViewLayer.start_transition_in()<ember.ui.ViewLayer.start_transition_in()>` is called 
        automatically when the ViewLayer loads.
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

        self.material_transition: Optional["Transition"] = material_transition
        """
        The Transition to use when changing Materials.
        """

        self.state_func: Callable[["ViewLayer"], "BackgroundState"] = state_func
        """
        The function that determines which state is active.
        Can be replaced for more control over the ViewLayer's states.
        """
