import pygame
from typing import Union, Optional, Sequence, Literal, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..ui.text_field import TextField

from .. import common as _c
from .style import Style, MaterialType

from ..state.state import State, load_state
from ..transition.transition import Transition

from ..size import SizeType, FILL
from . import defaults


def default_state_func(text_field: "TextField") -> State:
    if text_field._disabled:
        return text_field._style.disabled_state
    elif text_field.layer.element_focused is text_field:
        return text_field._style.active_state
    elif text_field.is_hovered:
        return text_field._style.hover_state
    else:
        return text_field._style.default_state


class TextFieldStyle(Style):
    def __init__(
        self,
        default_size: Sequence[SizeType] = (300, 80),
        default_scroll_size: Optional[Sequence[SizeType]] = None,
        default_h_scroll_size: Sequence[SizeType] = (FILL, FILL),
        default_v_scroll_size: Sequence[SizeType] = (FILL, FILL),
        default_state: Optional[State] = None,
        hover_state: Optional[State] = None,
        active_state: Optional[State] = None,
        disabled_state: Optional[State] = None,
        default_material: MaterialType = None,
        hover_material: MaterialType = None,
        active_material: MaterialType = None,
        disabled_material: MaterialType = None,
        cursor_blink_speed: float = 0.5,
        text_align: Literal["left", "center", "right"] = "center",
        text_fade: Union[pygame.Surface, str, None] = None,
        fade_width: Optional[int] = None,
        text_color: Union[str, tuple[int, int, int], pygame.Color, None] = None,
        prompt_color: Union[str, tuple[int, int, int], pygame.Color, None] = None,
        highlight_color: Union[str, tuple[int, int, int], pygame.Color] = (
            100,
            100,
            150,
        ),
        cursor_color: Union[str, tuple[int, int, int], pygame.Color] = (255, 255, 255),
        key_repeat_delay: float = 0.1,
        key_repeat_start_delay: float = 0.5,
        material_transition: Optional[Transition] = None,
        state_func: Optional[Callable[["TextField"], "State"]] = None,
    ):
        self.default_size: Sequence[SizeType] = default_size
        """
        The size of the TextField if no size is specified in the TextField constructor.
        """

        self.default_h_scroll_size: Sequence[SizeType] = (
            default_scroll_size if default_scroll_size else default_h_scroll_size
        )
        """
        The default size of the HScroll contained within the TextField.
        """
        self.default_v_scroll_size: Sequence[SizeType] = (
            default_scroll_size if default_scroll_size else default_v_scroll_size
        )
        """
        The default size of the VScroll contained within the TextField.
        """

        self.default_state: State = load_state(default_state, default_material, None)
        """
        The default State.
        """
        self.hover_state: State = load_state(
            hover_state, hover_material, self.default_state
        )
        """
        Shown when the TextField is hovered over. Uses the default state if no state is specified.
        """
        self.active_state: State = load_state(
            active_state, active_material, self.hover_state
        )
        """
        Shown when the TextField is active. Uses the hover state if no state is specified.
        """
        self.disabled_state: State = load_state(
            disabled_state, disabled_material, self.default_state
        )
        """
        Shown when the TextField is disabled. Uses the default state if no state is specified.
        """

        self.cursor_blink_speed: float = cursor_blink_speed
        """
        The time, in seconds, between each blink of the cursor.
        """
        self.text_align: Literal["left", "center", "right"] = text_align
        """
        The alignment of the text, if the Text object is constructed by the Textfield.
        """
        self.text_color = text_color
        """
        The color of the text, if the Text object is constructed by the TextField.
        """
        self.prompt_color = prompt_color if prompt_color is not None else text_color
        """
        The color of the prompt, if the prompt Text object is constructed by the TextField.
        """

        self.highlight_color: _c.ColorType = highlight_color

        self.cursor_color: _c.ColorType = cursor_color

        self.text_fade: pygame.Surface
        """
        An image used to fade out the text at either side of the TextField if multiline is off.
        """
        if text_fade:
            text_fade = (
                pygame.image.load(text_fade).convert_alpha()
                if type(text_fade) is str
                else text_fade
            )
            self.text_fade = pygame.transform.scale(
                text_fade, (text_fade.get_width(), 100)
            )
        elif fade_width:
            path = _c.package.joinpath(f"fonts/text_fade.png")
            self.text_fade = pygame.transform.scale(
                pygame.image.load(path), (fade_width, 100)
            )

        else:
            self.text_fade = pygame.Surface((1, 1), pygame.SRCALPHA)

        self.key_repeat_delay: float = key_repeat_delay
        """
        The delay in seconds between the repitition of keypresses.
        """
        self.key_repeat_start_delay: float = key_repeat_start_delay
        """
        The delay in seconds between the initial keypress and the first repitition.
        """

        self.material_transition: Optional[Transition] = material_transition
        """
        The Transition to use when changing States.
        """
        self.state_func: Callable[["TextField"], "State"] = (
            state_func if state_func is not None else default_state_func
        )
        """
        The function that determines which state is active. Can be replaced for more control over the TextField's states.
        """

    def set_as_default(self) -> "TextFieldStyle":
        defaults.text_field = self
        return self
