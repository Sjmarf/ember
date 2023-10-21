import pygame
from typing import Optional, TYPE_CHECKING
from ember.style.style import Style
from ember.style.state import State
from ember.ui.panel import Panel
from ember.material.material import Material
from ember.common import MaterialType
from ember.utility.load_material import load_material
from ember.size import OptionalSequenceSizeType, FILL
from ..size.ratio_size import RatioSize
from ember.position import LEFT, RIGHT
from ember.animation.ease import EaseInOut
from ember.event import (
    ELEMENTHOVERED,
    UNHOVERED,
    FOCUSED,
    ELEMENTUNFOCUSED,
    ENABLED,
    DISABLED,
    TOGGLEDON,
    TOGGLEDOFF,
)

from ember.ui.toggle_button import ToggleButton

if TYPE_CHECKING:
    from ember.animation.animation import Animation


class SwitchStyle(Style[ToggleButton]):
    def __init__(
        self,
        size: OptionalSequenceSizeType,
        handle_padding: int = 0,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
        default_handle_material: Optional[MaterialType] = None,
        hover_handle_material: Optional[MaterialType] = None,
        focus_handle_material: Optional[MaterialType] = None,
        disabled_handle_material: Optional[MaterialType] = None,
        animation: Optional["Animation"] = None,
    ):
        self.size: OptionalSequenceSizeType = size
        self.handle_padding: int = handle_padding

        self.animation = EaseInOut(0.2) if animation is None else animation

        self.default_material: Material = load_material(default_material, None)
        self.hover_material: Material = load_material(hover_material, self.default_material)
        self.focus_material: Material = load_material(focus_material, self.hover_material)
        self.disabled_material: Material = load_material(
            disabled_material, self.default_material
        )

        self.default_handle_material: Material = load_material(
            default_handle_material, None
        )
        self.hover_handle_material: Material = load_material(
            hover_handle_material, self.default_handle_material
        )
        self.focus_handle_material: Material = load_material(
            focus_handle_material, self.hover_handle_material
        )
        self.disabled_handle_material: Material = load_material(
            disabled_handle_material, self.default_handle_material
        )

        self.default_state: State["ToggleButton"] = State(
            active_by_default=True, on_become_primary=self.on_default
        )

        self.hover_state: State["ToggleButton"] = State(
            activation_triggers=[ELEMENTHOVERED],
            deactivation_triggers=[UNHOVERED],
            priority=1,
            on_become_primary=self.on_hover,
        )

        self.active_state: State["ToggleButton"] = State(
            activation_triggers=[TOGGLEDON],
            deactivation_triggers=[TOGGLEDOFF],
            on_become_active=self.on_toggled_on,
            on_become_deactive=self.on_toggled_off,
            priority=-1
        )

        self.focus_state: State["ToggleButton"] = State(
            activation_triggers=[FOCUSED],
            deactivation_triggers=[ELEMENTUNFOCUSED],
            priority=2,
            on_become_primary=self.on_focus,
        )
        self.disabled_state: State["ToggleButton"] = State(
            activation_triggers=[DISABLED],
            deactivation_triggers=[ENABLED],
            priority=3,
            on_become_primary=self.on_disabled,
        )

        self.default_state.on_become_primary_callable = self.on_default

        super().__init__(
            self.default_state,
            self.hover_state,
            self.focus_state,
            self.disabled_state,
            self.active_state
        )

    def _on_become_active(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        element.set_size(self.size)

        element.set_content_h(FILL)
        element.set_content_w(RatioSize())

        element.insert(0, Panel(self.default_material, size=FILL, pos=LEFT))
        element.insert(
            1,
            Panel(self.default_handle_material),
        )

        if element.active:
            element.set_content_x(RIGHT - self.handle_padding)
            self.active_state.activate()
        else:
            element.set_content_x(LEFT + self.handle_padding)

    def _on_become_deactive(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        del element[0]
        del element[1]

    def on_default(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        element[0].material = self.default_material
        element[1].material = self.default_handle_material

    def on_hover(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        element[0].material = self.hover_material
        element[1].material = self.hover_handle_material

    def on_focus(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        element[0].material = self.focus_material
        element[1].material = self.focus_handle_material

    def on_disabled(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        element[0].material = self.disabled_material
        element[1].material = self.disabled_handle_material

    def on_toggled_on(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        with self.animation:
            element.set_content_x(RIGHT - self.handle_padding)

    def on_toggled_off(self, element: "ToggleButton", event: Optional[pygame.Event]) -> None:
        with self.animation:
            element.set_content_x(LEFT + self.handle_padding)
