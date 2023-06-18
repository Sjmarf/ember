import pygame
from typing import TYPE_CHECKING, Optional, Sequence, Union

if TYPE_CHECKING:
    from ..style.scroll_style import ScrollStyle

from ..common import INHERIT, InheritType

from .. import log
from .. import common as _c
from .base.element import Element
from ..material.material import Material
from ..size import SizeType, SequenceSizeType
from ..position import PositionType, CENTER, SequencePositionType
from ..state.state import State

from .base.scroll import Scroll


class VScroll(Scroll):
    def __repr__(self) -> str:
        return "<VScroll>"

    def _render_scrollbar(
        self, surface: pygame.Surface, rect: pygame.Rect, alpha: int
    ) -> None:
        max_scroll = self._element.rect.h - self.rect.h + self.over_scroll[1]
        self._clamp_scroll_position(max_scroll)

        # Draw scrollbar
        if self.can_scroll:
            self.scrollbar_controller.set_state(
                self._style.scrollbar_state_func(self),
                transitions=(
                    self._style.base_material_transition,
                    self._style.handle_material_transition,
                ),
            )
            self.scrollbar_controller.render(
                surface,
                (rect.x + rect.w - self._style.scrollbar_size, rect.y),
                (self._style.scrollbar_size, rect.h),
                alpha,
                material_index=0,
            )

            self.scrollbar_controller.render(
                surface,
                (
                    rect.right - self._style.scrollbar_size,
                    rect.y + round(self._scrollbar_pos),
                ),
                (round(self._style.scrollbar_size), round(self._scrollbar_size + 1)),
                alpha,
                material_index=1,
            )

    def _update(self) -> None:
        if not self._element:
            return

        self._scrollbar_calc()
        element_h = self._element.get_abs_height(self.rect.h)
        max_scroll = element_h - self.rect.h + self.over_scroll[1]

        # Move the scrollbar if it's grabbed
        if self.scrollbar_grabbed:
            val = (_c.mouse_pos[1] - self.rect.y - self._scrollbar_grabbed_pos) / (
                self.rect.h - self._scrollbar_size
            ) * (max_scroll + self.over_scroll[0]) - self.over_scroll[0]

            self.scroll.val = val
            log.size.info(self, "Scrollbar is grabbed, starting chain down...")
            self._update_element_rect()

        if not self.can_scroll:
            max_scroll = 0

        self._clamp_scroll_position(max_scroll)

        # Update the element
        self._element._update_a()

        if self.scroll.tick():
            log.size.info(self, "Scroll is playing, starting chain down...")
            self._update_element_rect()

    def _update_element_rect(self) -> None:
        if self._element:
            with log.size.indent:
                padding = self._style.padding if self.can_scroll else 0

                if self.can_scroll:
                    element_y = self.rect.y - self.scroll.val
                    element_h = self.rect.h
                else:
                    element_y_obj = (
                        self._element._y
                        if self._element._y is not None
                        else self.content_y
                    )
                    element_h = self.rect.h - abs(element_y_obj.value)

                    element_y = self.rect.y + element_y_obj.get(
                        self.rect.h, self._element.get_abs_height(element_h)
                    )

                element_x_obj = (
                    self._element._x if self._element._x is not None else self.content_x
                )
                element_x = self.rect.x + element_x_obj.get(
                    self.rect.w - padding,
                    self._element.get_abs_width(
                        self.rect.w - abs(element_x_obj.value) - padding
                    ),
                )

                self._element.set_active_width(self.content_w)
                self._element.set_active_height(self.content_h)

                self._element._update_rect_chain_down(
                    self._subsurf,
                    element_x,
                    element_y,
                    self._element.get_abs_width(
                        self.rect.w - padding - abs(element_x_obj.value)
                    ),
                    self._element.get_abs_height(element_h),
                )

    def _event2(self, event: pygame.event.Event) -> bool:
        if self.scrollbar_hovered:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.scrollbar_grabbed = True
                self._scrollbar_grabbed_pos = _c.mouse_pos[1] - (
                    self.rect.y + self._scrollbar_pos
                )
                return True

        if event.type == pygame.MOUSEWHEEL and self.can_scroll:
            if self.rect.collidepoint(_c.mouse_pos):
                self.scroll.val = pygame.math.clamp(
                    self.scroll.val - event.y * self._style.scroll_speed,
                    -self.over_scroll[0],
                    self._element.rect.h - self.rect.h + self.over_scroll[1],
                )
                log.size.info(self, "Scrollwheel moved, starting chain down...")
                self._update_element_rect()
                return True
        return False

    def _scrollbar_calc(self) -> None:
        if not self._element:
            return
        element_h = self._element.get_abs_height(self.rect.h)
        max_scroll = element_h - self.rect.h + self.over_scroll[1]

        old_can_scroll = self.can_scroll

        # Scrollbar position and size calculations
        if not element_h:
            log.size.info(self, "Scrollbar disabled")
            self.can_scroll = False

        else:
            self._scrollbar_size = (
                self.rect.h
                / max(1.0, (element_h + self.over_scroll[0] + self.over_scroll[1]))
            ) * self.rect.h
            self.can_scroll = self._scrollbar_size < self.rect.h
            if old_can_scroll != self.can_scroll:
                log.size.info(
                    self,
                    f"Scrollbar {'enabled' if self.can_scroll else 'disabled'}, starting chain down...",
                )
                self._update_element_rect()

            if self.can_scroll:
                self._scrollbar_pos = (
                    (self.scroll.val + self.over_scroll[0])
                    / (max_scroll + self.over_scroll[0])
                ) * (self.rect.h - self._scrollbar_size)

                rect = pygame.Rect(
                    self.rect.right - self._style.scrollbar_size,
                    self.rect.y + self._scrollbar_pos,
                    self._style.scrollbar_size,
                    self._scrollbar_size,
                )
                self.scrollbar_hovered = rect.collidepoint(_c.mouse_pos)

        self._clamp_scroll_position(max_scroll)

    def scroll_to_show_position(
        self, position: int, size: int = 0, offset: int = 0, duration: float = 0.1
    ) -> None:
        if not self.can_scroll:
            log.size.info(
                self,
                f"Attempted scroll to show position, but cannot scroll. "
                f"Set scroll val to {self.over_scroll[0] * -1}.",
            )
            self.scroll.val = self.over_scroll[0] * -1
            self._update_element_rect()
            return
        if position - offset <= self.rect.y:
            position -= offset
            destination = self.scroll.val - (self.rect.y - position)
        elif position + size + offset > self.rect.bottom:
            position += offset
            destination = (
                self.scroll.val - (self.rect.y - position) - self.rect.h + size
            )
        else:
            return

        log.nav.info(self, f"Scrolling to position {position}.")

        destination = pygame.math.clamp(
            destination,
            -self.over_scroll[0],
            self._element.get_abs_height(self.rect.h)
            - self.rect.h
            + self.over_scroll[1],
        )
        if self.scroll.play(stop=destination, duration=duration):
            self._update_element_rect()
        self._scrollbar_calc()

    def scroll_to_element(self, element: Element) -> None:
        if not self.rect.contains(element.rect):
            log.nav.info(self, f"Scrolling so that {element} is visible.")
            self.scroll_to_show_position(element.rect.y, element.rect.h)
