from typing import Optional, TYPE_CHECKING

import pygame

from ember.style.style import Style
from ember.style.state import State
from ember.ui.panel import Panel
from ember.material.material import Material
from ember.common import MaterialType
from ember.utility.load_material import load_material
from ember.size import OptionalSequenceSizeType, FILL
from ..size.ratio_size import RatioSize
from ember.position import LEFT, AnchorPosition, TOPLEFT
from ember.animation.ease import EaseInOut
from ember.event import (
    ELEMENTHOVERED,
    ELEMENTUNHOVERED,
    ELEMENTFOCUSED,
    ELEMENTUNFOCUSED,
    ELEMENTENABLED,
    ELEMENTDISABLED,
    BUTTONDOWN,
    BUTTONUP,
    SLIDERMOVED,
    SLIDERCONTROLACTIVATED,
    SLIDERCONTROLDEACTIVATED,
)

from ember.base.slider import Slider

if TYPE_CHECKING:
    from ember.animation.animation import Animation


class SliderStyle(Style[Slider]):
    def __init__(
        self,
        size: OptionalSequenceSizeType,
        handle_padding: int = 0,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        click_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        focus_click_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
        default_handle_material: Optional[MaterialType] = None,
        hover_handle_material: Optional[MaterialType] = None,
        click_handle_material: Optional[MaterialType] = None,
        focus_handle_material: Optional[MaterialType] = None,
        focus_click_handle_material: Optional[MaterialType] = None,
        disabled_handle_material: Optional[MaterialType] = None,
        animation: Optional["Animation"] = None,
    ):
        self.size: OptionalSequenceSizeType = size
        self.handle_padding: int = handle_padding

        self.animation = EaseInOut(0.2) if animation is None else animation

        self.default_material: Material = load_material(default_material, None)
        self.hover_material: Material = load_material(
            hover_material, self.default_material
        )
        self.click_material: Material = load_material(
            click_material, self.hover_material
        )
        self.focus_material: Material = load_material(
            focus_material, self.hover_material
        )
        self.focus_click_material: Material = load_material(
            focus_click_material, self.focus_material
        )
        self.disabled_material: Material = load_material(
            disabled_material, self.default_material
        )

        self.default_handle_material: Material = load_material(
            default_handle_material, None
        )
        self.hover_handle_material: Material = load_material(
            hover_handle_material, self.default_handle_material
        )
        self.click_handle_material: Material = load_material(
            click_handle_material, self.hover_handle_material
        )
        self.focus_handle_material: Material = load_material(
            focus_handle_material, self.hover_handle_material
        )
        self.focus_click_handle_material: Material = load_material(
            focus_click_handle_material, self.focus_handle_material
        )
        self.disabled_handle_material: Material = load_material(
            disabled_handle_material, self.default_handle_material
        )

        self.default_state: State["Slider"] = State(
            active_by_default=True, on_become_primary=self.on_default, name="default"
        )

        self.hover_state: State["Slider"] = State(
            activation_triggers=[ELEMENTHOVERED],
            deactivation_triggers=[ELEMENTUNHOVERED],
            priority=1,
            on_become_primary=self.on_hover,
            name="hover",
        )

        self.click_state: State["Slider"] = State(
            activation_triggers=[BUTTONDOWN, SLIDERCONTROLACTIVATED],
            deactivation_triggers=[BUTTONUP, SLIDERCONTROLDEACTIVATED],
            priority=3,
            on_become_primary=self.on_click,
            name="click",
        )

        self.focus_state: State["Slider"] = State(
            activation_triggers=[ELEMENTFOCUSED],
            deactivation_triggers=[ELEMENTUNFOCUSED],
            priority=2,
            on_become_primary=self.on_focus,
            name="focus",
        )

        self.disabled_state: State["Slider"] = State(
            activation_triggers=[ELEMENTDISABLED],
            deactivation_triggers=[ELEMENTENABLED],
            priority=4,
            on_become_primary=self.on_disabled,
            name="disabled",
        )

        self.default_state.on_become_primary_callable = self.on_default

        super().__init__(
            self.default_state,
            self.hover_state,
            self.focus_state,
            self.click_state,
            self.disabled_state,
        )

        self.add_event_callback(self.on_move, SLIDERMOVED)

    def _on_become_active(self, element: "Slider", event: Optional[pygame.Event]) -> None:
        element.set_parallel_size(self.size[0])
        element.set_perpendicular_size(self.size[1])

        element.set_perpendicular_content_size(FILL - self.handle_padding * 2)
        element.set_parallel_content_size(RatioSize())

        element.insert(0, Panel(self.default_material, size=FILL, pos=TOPLEFT))
        element.insert(
            1,
            Panel(self.default_handle_material),
        )

        element.set_parallel_content_pos(LEFT + self.handle_padding)
        element.set_perpendicular_content_pos(self.handle_padding)

    def _on_become_deactive(
        self, element: "Slider", event: Optional[pygame.Event]
    ) -> None:
        del element[0]
        del element[1]

    def on_default(self, element: "Slider", event: Optional[pygame.Event]) -> None:
        element[0].material = self.default_material
        element[1].material = self.default_handle_material

    def on_hover(self, element: "Slider", event: Optional[pygame.Event]) -> None:
        element[0].material = self.hover_material
        element[1].material = self.hover_handle_material

    def on_focus(self, element: "Slider", event: Optional[pygame.Event]) -> None:
        element[0].material = self.focus_material
        element[1].material = self.focus_handle_material

    def on_disabled(self, element: "Slider", event: Optional[pygame.Event]) -> None:
        element[0].material = self.disabled_material
        element[1].material = self.disabled_handle_material

    def on_click(self, element: "Slider", event: Optional[pygame.Event]) -> None:
        element[0].material = (
            self.focus_click_material
            if self.focus_state.is_active()
            else self.click_material
        )
        element[1].material = (
            self.focus_click_handle_material
            if self.focus_state.is_active()
            else self.click_handle_material
        )

    def on_move(self, element: "Slider", event: Optional[pygame.Event]) -> None:
        if event is not None and event.cause in {
            element.MovementCause.CLICK,
            element.MovementCause.SET,
        }:
            with self.animation:
                element.set_parallel_content_pos(AnchorPosition(0, element.progress))
        else:
            element.set_parallel_content_pos(AnchorPosition(0, element.progress))
