import pygame
from typing import Union, Optional, Sequence, TYPE_CHECKING, Callable

from .. import common as _c
from .style import Style, MaterialType
from ..state.state import State, load_state
from ..transition.transition import Transition
from . import defaults

if TYPE_CHECKING:
    from ..ui.button import Button

from .text_style import TextStyle
from .load_material import load_sound
from ..size import SizeType


def default_state_func(button: "Button") -> State:
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


class ButtonStyle(Style):
    def __init__(
        self,
        default_size: Sequence[SizeType] = (300, 80),
        default_state: Optional[State] = None,
        hover_state: Optional[State] = None,
        click_state: Optional[State] = None,
        focus_state: Optional[State] = None,
        focus_click_state: Optional[State] = None,
        disabled_state: Optional[State] = None,
        default_material: MaterialType = None,
        hover_material: MaterialType = None,
        click_material: MaterialType = None,
        focus_material: MaterialType = None,
        focus_click_material: MaterialType = None,
        disabled_material: MaterialType = None,
        click_down_sound: Union[pygame.mixer.Sound, str, None] = None,
        click_up_sound: Union[pygame.mixer.Sound, str, None] = None,
        text_style: Optional[TextStyle] = None,
        material_transition: Optional[Transition] = None,
        state_func: Optional[Callable[["Button"], "State"]] = None,
    ):
        self.default_size: Sequence[SizeType] = default_size
        """
        The size of the Button if no size is specified in the Button constructor.
        """

        self.default_state: State = load_state(default_state, default_material, None)
        """
        The default State.
        """
        self.hover_state: State = load_state(
            hover_state, hover_material, self.default_state
        )
        """
        Shown when the Button is hovered over. Uses the default state if no state is specified.
        """
        self.click_state: State = load_state(
            click_state, click_material, self.hover_state
        )
        """
        Shown when the Button is clicked. Uses the hover state if no state is specified.
        """
        self.focus_state: State = load_state(
            focus_state, focus_material, self.hover_state
        )
        """
        Shown when the Button is focused. Uses the hover state if no state is specified.
        """
        self.focus_click_state: State = load_state(
            focus_click_state, focus_click_material, self.click_state
        )
        """
        Shown when the Button is focused and clicked. Uses the click state if no state is specified.
        """
        self.disabled_state: State = load_state(
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

        self.state_func: Callable[["Button"], "State"] = (
            state_func if state_func is not None else default_state_func
        )
        """
        The function that determines which state is active. Can be replaced for more control over the Button's states.
        """

    def set_as_default(self) -> "ButtonStyle":
        defaults.button = self
        return self
