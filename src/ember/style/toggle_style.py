import pygame
from typing import Optional, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ..ui.toggle import Toggle

from .. import common as _c
from ..common import MaterialType
from .style import Style
from ..size import SizeType, SequenceSizeType
from ..state.toggle_state import ToggleState

from ember.utility.load_material import load_sound
from ..transition.transition import Transition
from ..ui.toggle import Toggle


class ToggleStyle(Style):
    _ELEMENT = Toggle

    @staticmethod
    def default_state_func(toggle: "Toggle") -> ToggleState:
        if toggle._disabled:
            return toggle._style.disabled_state
        if toggle.layer.element_focused is toggle:
            return toggle._style.focus_state
        elif toggle.is_hovered:
            return toggle._style.hover_state
        else:
            return toggle._style.default_state

    def __init__(
        self,
        size: SequenceSizeType = (200, 80),
        width: SizeType = None,
        height: SizeType = None,
        handle_width_ratio: float = 1,
        default_state: Optional[ToggleState] = None,
        hover_state: Optional[ToggleState] = None,
        focus_state: Optional[ToggleState] = None,
        disabled_state: Optional[ToggleState] = None,
        default_base_material: Optional[MaterialType] = None,
        default_handle_material: Optional[MaterialType] = None,
        hover_handle_material: Optional[MaterialType] = None,
        focus_handle_material: Optional[MaterialType] = None,
        disabled_handle_material: Optional[MaterialType] = None,
        switch_on_sound: Optional[pygame.mixer.Sound] = None,
        switch_off_sound: Optional[pygame.mixer.Sound] = None,
        handle_material_transition: Optional[Transition] = None,
        base_material_transition: Optional[Transition] = None,
        state_func: Callable[["Toggle"], "ToggleState"] = default_state_func,
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Element if no size is specified in the Element constructor.
        """

        self.handle_width_ratio: float = handle_width_ratio
        """
        Modifies the ratio between the handle width and height. toggle_height * handle_width_ratio = handle_width
        """

        self.default_state: ToggleState = ToggleState._load(
            default_state, default_base_material, default_handle_material
        )
        """
        The default State of the Toggle.
        """
        self.hover_state: ToggleState = ToggleState._load(
            hover_state, None, hover_handle_material, self.default_state
        )
        """
        Shown when the Toggle is hovered over. Uses the default state if no state is specified.
        """
        self.focus_state: ToggleState = ToggleState._load(
            focus_state, None, focus_handle_material, self.hover_state
        )
        """
        Shown when the Toggle is focused. Uses the hover state if no state is specified.
        """
        self.disabled_state: ToggleState = ToggleState._load(
            disabled_state, None, disabled_handle_material, self.default_state
        )
        """
        Shown when the Toggle is disabled. Uses the default state if no state is specified.
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

        self.handle_material_transition: Optional[
            Transition
        ] = handle_material_transition
        """
        The Transition to use when changing handle Materials.
        """
        self.base_material_transition: Optional[Transition] = base_material_transition
        """
        The Transition to use when changing base Materials.
        """

        self.state_func: Callable[["Toggle"], "ToggleState"] = state_func
        """
        The function that determines which state is active. Can be replaced for more control over the Toggle's states.
        """
