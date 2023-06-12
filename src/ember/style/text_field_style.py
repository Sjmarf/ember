import pygame
from typing import Union, Optional, Sequence, Literal, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..ui.text_field import TextField

from .. import common as _c
from ..common import ColorType, MaterialType
from .style import Style

from ..state.text_field_state import TextFieldState
from ..transition.transition import Transition

from ..size import SizeType, FILL, SequenceSizeType
from ..position import Position, CENTER
from ..ui.text_field import TextField

from ..style.text_style import TextStyle
from ..style.scroll_style import ScrollStyle

class TextFieldStyle(Style):
    _ELEMENT = TextField

    @staticmethod
    def default_state_func(text_field: "TextField") -> TextFieldState:
        if text_field._disabled:
            return text_field._style.disabled_state
        elif text_field.layer.element_focused is text_field:
            return text_field._style.active_state
        elif text_field.is_hovered:
            return text_field._style.hover_state
        else:
            return text_field._style.default_state

    def __init__(
        self,
        size: SequenceSizeType = (300, 80),
        width: SizeType = None,
        height: SizeType = None,
        default_scroll_size: Optional[Sequence[SizeType]] = None,
        default_h_scroll_size: Optional[Sequence[SizeType]] = (FILL, FILL),
        default_v_scroll_size: Optional[Sequence[SizeType]] = (FILL, FILL),
        default_state: Optional[TextFieldState] = None,
        hover_state: Optional[TextFieldState] = None,
        active_state: Optional[TextFieldState] = None,
        disabled_state: Optional[TextFieldState] = None,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        active_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
        cursor_blink_speed: float = 0.5,
        text_style: Optional[TextStyle] = None,
        prompt_style: Optional[TextStyle] = None,
        scroll_style: Optional[ScrollStyle] = None,
        text_align: Sequence[Position] = (CENTER, CENTER),
        text_fade: Union[pygame.Surface, str, None] = None,
        fade_width: Optional[int] = None,
        highlight_color: ColorType = (100, 100, 150),
        cursor_color: ColorType = (255, 255, 255),
        key_repeat_delay: float = 0.1,
        key_repeat_start_delay: float = 0.5,
        material_transition: Optional[Transition] = None,
        state_func: Callable[["TextField"], "TextFieldState"] = default_state_func,
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Element if no size is specified in the Element constructor.
        """

        self.default_h_scroll_size: Optional[Sequence[SizeType]] = (
            default_scroll_size if default_scroll_size else default_h_scroll_size
        )
        """
        The default size of the HScroll contained within the TextField.
        """
        self.default_v_scroll_size: Optional[Sequence[SizeType]] = (
            default_scroll_size if default_scroll_size else default_v_scroll_size
        )
        """
        The default size of the VScroll contained within the TextField.
        """

        self.default_state: TextFieldState = TextFieldState._load(default_state, default_material)
        """
        The default State.
        """
        self.hover_state: TextFieldState = TextFieldState._load(
            hover_state, hover_material, self.default_state
        )
        """
        Shown when the TextField is hovered over. Uses the default state if no state is specified.
        """
        self.active_state: TextFieldState = TextFieldState._load(
            active_state, active_material, self.hover_state
        )
        """
        Shown when the TextField is active. Uses the hover state if no state is specified.
        """
        self.disabled_state: TextFieldState = TextFieldState._load(
            disabled_state, disabled_material, self.default_state
        )
        """
        Shown when the TextField is disabled. Uses the default state if no state is specified.
        """

        self.cursor_blink_speed: float = cursor_blink_speed
        """
        The time, in seconds, between each blink of the cursor.
        """

        self.scroll_style: ScrollStyle = scroll_style
        """
        The Scroll style used for the Scroll element if it is contructed by the TextField.
        """

        self.text_style: TextStyle = text_style
        """
        The Text style used for the Text element if it is contructed by the TextField.
        """

        self.prompt_style: TextStyle = prompt_style
        """
        The Text style used for the prompt Text element if it is contructed by the TextField.
        """

        self.highlight_color: _c.ColorType = highlight_color

        self.cursor_color: _c.ColorType = cursor_color

        self.text_align: str = text_align
        """
        The alignment of the text in the TextField.
        """

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
        self.state_func: Callable[["TextField"], "TextFieldState"] = state_func
        """
        The function that determines which state is active. Can be replaced for more control over the TextField's states.
        """
