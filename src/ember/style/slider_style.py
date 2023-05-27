from typing import Optional, Sequence, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..ui.slider import Slider

from .. import common as _c
from .style import Style, MaterialType

from ..state.state import State, load_state
from ..transition.transition import Transition
from ..size import SizeType
from . import defaults


def default_base_state_func(slider: "Slider") -> State:
    return slider._style.default_base_state


def default_state_func(slider: "Slider") -> State:
    if slider._disabled:
        return slider._style.disabled_state
    if slider.layer.element_focused is slider:
        return (
            slider._style.focus_click_state
            if slider.is_clicked or slider.is_clicked_keyboard
            else slider._style.focus_state
        )
    if slider.is_clicked:
        return slider._style.click_state
    if slider.is_hovered:
        return slider._style.hover_state
    return slider._style.default_state


class SliderStyle(Style):
    def __init__(
        self,
        default_size: Sequence[SizeType] = (500, 80),
        handle_width_ratio: float = 1,
        default_base_state: Optional[State] = None,
        default_state: Optional[State] = None,
        hover_state: Optional[State] = None,
        click_state: Optional[State] = None,
        focus_state: Optional[State] = None,
        focus_click_state: Optional[State] = None,
        disabled_state: Optional[State] = None,
        default_base_material: MaterialType = None,
        default_material: MaterialType = None,
        hover_material: MaterialType = None,
        click_material: MaterialType = None,
        focus_material: MaterialType = None,
        focus_click_material: MaterialType = None,
        disabled_material: MaterialType = None,
        material_transition: Optional[Transition] = None,
        base_material_transition: Optional[Transition] = None,
        state_func: Optional[Callable[["Toggle"], "State"]] = None,
        base_state_func: Optional[Callable[["Toggle"], "State"]] = None,
    ):
        self.default_size: Sequence[SizeType] = default_size
        """
        The size of the Slider if no size is specified in the Slider constructor.
        """

        self.handle_width_ratio: float = handle_width_ratio
        """
        Modifies the ratio between the handle width and height. slider_height * handle_width_ratio = handle_width
        """

        self.default_base_state: State = load_state(
            default_base_state, default_base_material, None
        )
        """
        The default State of the Slider base.
        """

        self.default_state: State = load_state(default_state, default_material, None)
        """
        The default State of the Slider handle.
        """

        self.hover_state: State = load_state(
            hover_state, hover_material, self.default_state
        )
        """
        Shown when the Slider handle is hovered over. Uses the default state if no state is specified.
        """
        self.click_state: State = load_state(
            click_state, click_material, self.hover_state
        )
        """
        Shown when the Slider handle is clicked. Uses the hover state if no state is specified.
        """
        self.focus_state: State = load_state(
            focus_state, focus_material, self.hover_state
        )
        """
        Shown when the Slider handle is focused. Uses the hover state if no state is specified.
        """
        self.focus_click_state: State = load_state(
            focus_click_state, focus_click_material, self.focus_state
        )
        """
        Shown when the Slider handle is focused and clicked. Uses the click state if no state is specified.
        """
        self.disabled_state: State = load_state(
            disabled_state, disabled_material, self.default_state
        )
        """
        Shown when the Slider handle is disabled. Uses the default state if no state is specified.
        """

        self.material_transition: Optional[Transition] = material_transition
        """
        The Transition to use when changing handle States.
        """
        self.base_material_transition: Optional[Transition] = base_material_transition
        """
        The Transition to use when changing base States.
        """

        self.state_func: Callable[["Slider"], "State"] = (
            state_func if state_func is not None else default_state_func
        )
        """
        The function that determines which handle state is active. Can be replaced for more control over the Slider's handle states.
        """
        self.base_state_func: Callable[["Slider"], "State"] = (
            base_state_func if base_state_func is not None else default_base_state_func
        )
        """
        The function that determines which base state is active. Can be replaced for more control over the Slider's base states.
        """

    def set_as_default(self) -> "SliderStyle":
        defaults.slider = self
        return self
