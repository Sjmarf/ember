import pygame
from typing import Union, Optional, TYPE_CHECKING, Callable, Sequence

from .. import common as _c
from ..common import MaterialType
from .style import Style
from ..state.button_state import ButtonState
from ..transition.transition import Transition
from ..size import OptionalSequenceSizeType, Size
from ..position import SequencePositionType, CENTER, Position

if TYPE_CHECKING:
    from ..ui.button import Button

from .text_style import TextStyle
from ember.utility.load_material import load_sound
from ..size import SizeType, SequenceSizeType
from ..ui.button import Button


class ButtonStyle(Style):
    _ELEMENT = Button

    @staticmethod
    def default_state_func(button: "Button") -> ButtonState:
        if button._disabled:
            return button._style.disabled_state
        elif button.is_clicked:
            return (
                button._style.focus_click_state
                if button.layer.element_focused is button
                else button._style.click_state
            )
        elif button.layer.element_focused is button:
            return button._style.focus_state
        elif button.is_hovered:
            return button._style.hover_state
        else:
            return button._style.default_state

    def __init__(
        self,
        size: SequenceSizeType = (300, 80),
        width: SizeType = None,
        height: SizeType = None,
        content_pos: SequencePositionType = CENTER,
        content_size: OptionalSequenceSizeType = None,
        default_state: Optional[ButtonState] = None,
        hover_state: Optional[ButtonState] = None,
        click_state: Optional[ButtonState] = None,
        focus_state: Optional[ButtonState] = None,
        focus_click_state: Optional[ButtonState] = None,
        disabled_state: Optional[ButtonState] = None,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        click_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        focus_click_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
        click_down_sound: Union[pygame.mixer.Sound, str, None] = None,
        click_up_sound: Union[pygame.mixer.Sound, str, None] = None,
        text_style: Optional[TextStyle] = None,
        material_transition: Optional[Transition] = None,
        state_func: Callable[["Button"], "ButtonState"] = default_state_func,
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Element if no size is specified in the Element constructor.
        """

        if not isinstance(content_pos, Sequence):
            content_pos = (content_pos, content_pos)

        self.content_pos: Sequence[Position] = content_pos
        """
        The alignment of elements within the button.
        """

        if not isinstance(content_size, Sequence):
            content_size = (content_size, content_size)

        self.content_size: Sequence[Optional[Size]] = content_size
        """
        The size of elements within the button.
        """

        self.default_state: ButtonState = ButtonState._load(
            default_state, default_material
        )
        """
        The default State.
        """
        self.hover_state: ButtonState = ButtonState._load(
            hover_state, hover_material, self.default_state
        )
        """
        Shown when the Button is hovered over. Uses the default state if no state is specified.
        """
        self.click_state: ButtonState = ButtonState._load(
            click_state, click_material, self.hover_state
        )
        """
        Shown when the Button is clicked. Uses the hover state if no state is specified.
        """
        self.focus_state: ButtonState = ButtonState._load(
            focus_state, focus_material, self.hover_state
        )
        """
        Shown when the Button is focused. Uses the hover state if no state is specified.
        """
        self.focus_click_state: ButtonState = ButtonState._load(
            focus_click_state, focus_click_material, self.click_state
        )
        """
        Shown when the Button is focused and clicked. Uses the click state if no state is specified.
        """
        self.disabled_state: ButtonState = ButtonState._load(
            disabled_state, disabled_material, self.default_state
        )
        """
        Shown when the Button is disabled. Uses the default state if no state is specified.
        """

        self.click_down_sound: Optional[pygame.mixer.Sound]
        """
        The sound to play when the Button is clicked down.
        """

        self.click_up_sound: Optional[pygame.mixer.Sound]
        """
        The sound to play when the Button is clicked up.
        """

        if _c.audio_enabled:
            self.click_down_sound: Optional[pygame.mixer.Sound] = load_sound(
                click_down_sound
            )
            self.click_up_sound: Optional[pygame.mixer.Sound] = load_sound(
                click_up_sound
            )
        else:
            self.click_down_sound: Optional[pygame.mixer.Sound] = None
            self.click_up_sound: Optional[pygame.mixer.Sound] = None

        self.text_style: TextStyle = text_style
        """
        The TextStyle to apply to the Text object if a string is passed to the Button constructor.
        """

        self.material_transition: Optional[Transition] = material_transition
        """
        The Transition to use when changing States.
        """

        self.state_func: Callable[["Button"], "ButtonState"] = state_func
        """
        The function that determines which state is active. Can be replaced for more control over the Button's states.
        """
