import pygame
from typing import Optional, TYPE_CHECKING, Generic
from ..style.style import Style
from ..style.state import State
from ..ui.panel import Panel
from ..material.material import Material
from ..common import MaterialType
from ..utility.load_material import load_material
from ..size import OptionalSequenceSizeType, FILL, SizeType
from ..event import (
    BUTTONDOWN,
    BUTTONUP,
    ELEMENTHOVERED,
    ELEMENTUNHOVERED,
    ELEMENTFOCUSED,
    ELEMENTUNFOCUSED,
    ELEMENTENABLED,
    ELEMENTDISABLED,
)

from ..ui.Button import Button
from .style import Style


class ButtonStyle(Style[Button]):

    def __init__(
        self,
        size: OptionalSequenceSizeType = None,
        content_size: OptionalSequenceSizeType = None,
        content_y: Optional[SizeType] = None,
        content_y_clicked: Optional[SizeType] = None,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        click_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        focus_click_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
    ):
        self.size: OptionalSequenceSizeType = size
        self.content_size: OptionalSequenceSizeType = content_size
        self.content_y: Optional[SizeType] = content_y
        self.content_y_clicked: Optional[SizeType] = content_y_clicked

        self.default_material: Material = load_material(default_material, None)
        self.hover_material: Material = load_material(hover_material, self.default_material)
        self.click_material: Material = load_material(click_material, self.hover_material)
        self.focus_material: Material = load_material(focus_material, self.hover_material)
        self.focus_click_material: Material = load_material(
            focus_click_material, self.click_material
        )
        self.disabled_material: Material = load_material(
            disabled_material, self.default_material
        )

        self.default_state: State["Button"] = State(
            active_by_default=True, on_become_primary=self.on_default
        )

        self.hover_state: State["Button"] = State(
            activation_triggers=[ELEMENTHOVERED],
            deactivation_triggers=[ELEMENTUNHOVERED],
            priority=1,
            on_become_primary=self.on_hover,
        )
        self.click_state: State["Button"] = State(
            activation_triggers=[BUTTONDOWN],
            deactivation_triggers=[BUTTONUP, ELEMENTUNFOCUSED],
            priority=3,
            on_become_active=self.on_click_down,
            on_become_deactive=self.on_click_up,
        )
        self.focus_state: State["Button"] = State(
            activation_triggers=[ELEMENTFOCUSED],
            deactivation_triggers=[ELEMENTUNFOCUSED],
            priority=2,
            on_become_primary=self.on_focus,
        )
        self.disabled_state: State["Button"] = State(
            activation_triggers=[ELEMENTDISABLED],
            deactivation_triggers=[ELEMENTENABLED],
            priority=3,
            on_become_primary=self.on_disabled,
        )

        self.default_state.on_become_primary_callable = self.on_default

        super().__init__(
            self.default_state,
            self.hover_state,
            self.click_state,
            self.focus_state,
            self.disabled_state,
        )

    def _on_become_active(self, element: "Button", event: Optional[pygame.Event]) -> None:
        element.set_size(self.size)
        element.set_content_size(self.content_size)
        element.set_content_y(self.content_y)
        element.insert(0, Panel(size=FILL, pos=0))

    def _on_become_deactive(self, element: "Button", event: Optional[pygame.Event]) -> None:
        del element[0]

    def on_default(self, element: "Button", event: Optional[pygame.Event]) -> None:
        element[0].material = self.default_material

    def on_hover(self, element: "Button", event: Optional[pygame.Event]) -> None:
        element[0].material = self.hover_material

    def on_click_down(self, element: "Button", event: Optional[pygame.Event]) -> None:
        element[0].material = (
            self.focus_click_material
            if self.focus_state.is_active()
            else self.click_material
        )
        element.set_content_y(self.content_y_clicked)

    def on_click_up(self, element: "Button", event: Optional[pygame.Event]) -> None:
        element.set_content_y(self.content_y)

    def on_focus(self, element: "Button", event: Optional[pygame.Event]) -> None:
        element[0].material = self.focus_material

    def on_disabled(self, element: "Button", event: Optional[pygame.Event]) -> None:
        element[0].material = self.disabled_material
