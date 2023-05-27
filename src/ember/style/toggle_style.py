import pygame
from typing import Optional, Sequence, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..ui.toggle import Toggle

from .. import common as _c
from .style import Style, MaterialType
from ..size import SizeType
from ..state.state import State, load_state

from .load_material import load_sound
from ..transition.transition import Transition
from . import defaults


def default_base_state_func(toggle: "Toggle") -> State:
    return toggle.style.default_base_state


def default_state_func(toggle: "Toggle") -> State:
    if toggle._disabled:
        return toggle._style.disabled_state
    if toggle.layer.element_focused is toggle:
        return toggle._style.focus_state
    elif toggle.is_hovered:
        return toggle._style.hover_state
    else:
        return toggle._style.default_state


class ToggleStyle(Style):
    def __init__(
        self,
        default_size: Sequence[SizeType] = (300, 80),
        handle_width_ratio: float = 1,
        default_base_state: Optional[State] = None,
        default_state: Optional[State] = None,
        hover_state: Optional[State] = None,
        focus_state: Optional[State] = None,
        disabled_state: Optional[State] = None,
        default_base_material: MaterialType = None,
        default_material: MaterialType = None,
        hover_material: MaterialType = None,
        focus_material: MaterialType = None,
        disabled_material: MaterialType = None,
        switch_on_sound: Optional[pygame.mixer.Sound] = None,
        switch_off_sound: Optional[pygame.mixer.Sound] = None,
        material_transition: Optional[Transition] = None,
        base_material_transition: Optional[Transition] = None,
        state_func: Optional[Callable[["Toggle"], "State"]] = None,
        base_state_func: Optional[Callable[["Toggle"], "State"]] = None,
    ):
        self.default_size: Sequence[SizeType] = default_size
        """
        The size of the Toggle if no size is specified in the Toggle constructor.
        """

        self.handle_width_ratio: float = handle_width_ratio
        """
        Modifies the ratio between the handle width and height. toggle_height * handle_width_ratio = handle_width
        """

        self.default_base_state: State = load_state(
            default_base_state, default_base_material, None
        )
        """
        The default State of the Toggle base.
        """
        self.default_state: State = load_state(default_state, default_material, None)
        """
        The default State of the Toggle handle.
        """
        self.hover_state: State = load_state(
            hover_state, hover_material, self.default_state
        )
        """
        Shown when the Toggle handle is hovered over. Uses the default state if no state is specified.
        """
        self.focus_state: State = load_state(
            focus_state, focus_material, self.hover_state
        )
        """
        Shown when the Toggle handle is focused. Uses the hover state if no state is specified.
        """
        self.disabled_state: State = load_state(
            disabled_state, disabled_material, self.default_state
        )
        """
        Shown when the Toggle handle is disabled. Uses the default state if no state is specified.
        """

        self.switch_on_sound: Optional[pygame.mixer.Sound]
        """
        The sound to play when the Toggle is switched on.
        """

        self.switch_off_sound: Optional[pygame.mixer.Sound]
        """
        The sound to play when the Toggle is switched off.
        """

        if _c.audio_enabled:
            self.switch_on_sound: Optional[pygame.mixer.Sound] = load_sound(
                switch_on_sound
            )
            self.switch_off_sound: Optional[pygame.mixer.Sound] = load_sound(
                switch_off_sound
            )
        else:
            self.switch_on_sound: Optional[pygame.mixer.Sound] = None
            self.switch_off_sound: Optional[pygame.mixer.Sound] = None

        self.material_transition: Optional[Transition] = material_transition
        """
        The Transition to use when changing handle States.
        """
        self.base_material_transition: Optional[Transition] = base_material_transition
        """
        The Transition to use when changing base States.
        """

        self.state_func: Callable[["Toggle"], "State"] = (
            state_func if state_func is not None else default_state_func
        )
        """
        The function that determines which handle state is active. Can be replaced for more control over the Toggle's handle states.
        """
        self.base_state_func: Callable[["Toggle"], "State"] = (
            base_state_func if base_state_func is not None else default_base_state_func
        )
        """
        The function that determines which base state is active. Can be replaced for more control over the Toggle's base states.
        """

    def set_as_default(self) -> "ToggleStyle":
        defaults.toggle = self
        return self
