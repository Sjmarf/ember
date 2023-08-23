from typing import Optional, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ember.ui.base.slider import Slider

from ..common import MaterialType
from .style import Style

from ember.style.state import SliderState

from ..size import SizeType, SequenceSizeType
from ember.ui.base.slider import Slider


class SliderStyle(Style):
    _ELEMENT = Slider

    @staticmethod
    def default_state_func(slider: "Slider") -> SliderState:
        if slider._disabled:
            return slider._style.disabled_state
        if slider.layer.element_focused is slider:
            return (
                slider._style.focus_click_state
                if slider.is_clicked or slider.is_clicked_keyboard
                else slider._style.focus_state
            )
        if slider.is_clicked:
            return slider._style.click_handle_state
        if slider.is_hovered:
            return slider._style.hover_handle_state
        return slider._style.default_handle_state

    def __init__(
        self,
        size: SequenceSizeType = (300, 80),
        width: SizeType = None,
        height: SizeType = None,
        handle_width_ratio: float = 1,
        default_state: Optional[SliderState] = None,
        hover_state: Optional[SliderState] = None,
        click_state: Optional[SliderState] = None,
        focus_state: Optional[SliderState] = None,
        focus_click_state: Optional[SliderState] = None,
        disabled_state: Optional[SliderState] = None,
        default_base_material: Optional[MaterialType] = None,
        default_handle_material: Optional[MaterialType] = None,
        hover_handle_material: Optional[MaterialType] = None,
        click_handle_material: Optional[MaterialType] = None,
        focus_handle_material: Optional[MaterialType] = None,
        focus_click_handle_material: Optional[MaterialType] = None,
        disabled_handle_material: Optional[MaterialType] = None,
        handle_material_transition: Optional["Transition"] = None,
        base_material_transition: Optional["Transition"] = None,
        state_func: Callable[
            ["Slider"], "SliderState"
        ] = default_state_func,
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Element if no size is specified in the Element constructor.
        """

        self.handle_width_ratio: float = handle_width_ratio
        """
        Modifies the ratio between the handle width and height. slider_height * handle_width_ratio = handle_width
        """

        self.default_handle_state: SliderState = SliderState._load(
            default_state, default_base_material, default_handle_material
        )
        """
        The default State of the Slider.
        """

        self.hover_handle_state: SliderState = SliderState._load(
            hover_state, None, hover_handle_material, self.default_handle_state
        )
        """
        Shown when the Slider is hovered over. Uses the default state if no state is specified.
        """
        self.click_handle_state: SliderState = SliderState._load(
            click_state, None, click_handle_material, self.hover_handle_state
        )
        """
        Shown when the Slider is clicked. Uses the hover state if no state is specified.
        """
        self.focus_state: SliderState = SliderState._load(
            focus_state, None, focus_handle_material, self.hover_handle_state
        )
        """
        Shown when the Slider is focused. Uses the hover state if no state is specified.
        """
        self.focus_click_state: SliderState = SliderState._load(
            focus_click_state, None, focus_click_handle_material, self.focus_state
        )
        """
        Shown when the Slider is focused and clicked. Uses the click state if no state is specified.
        """
        self.disabled_state: SliderState = SliderState._load(
            disabled_state, None, disabled_handle_material, self.default_handle_state
        )
        """
        Shown when the Slider is disabled. Uses the default state if no state is specified.
        """

        self.handle_material_transition: Optional[
            Transition
        ] = handle_material_transition
        """
        The Transition to use when changing handle Materials.
        """
        self.base_material_transition: Optional["Transition"] = base_material_transition
        """
        The Transition to use when changing base Materials.
        """

        self.state_func: Callable[["Slider"], "SliderState"] = state_func
        """
        The function that determines which state is active. Can be replaced for more control over the Slider's states.
        """
