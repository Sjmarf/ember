import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .. import log
from .. import common as _c
from .base.element import Element

from .base.scroll import Scroll


class HScroll(Scroll):
    def __repr__(self) -> str:
        return "<HScroll>"

    def _render_scrollbar(
        self, surface: pygame.Surface, rect: pygame.Rect, alpha: int
    ) -> None:
        max_scroll = self._element.rect.w - self.rect.w + self.over_scroll[1]
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
                (rect.x, rect.y + rect.h - self._style.scrollbar_size),
                (rect.w, self._style.scrollbar_size),
                alpha,
                material_index=0,
            )

            self.scrollbar_controller.render(
                surface,
                (
                    rect.x - surface.get_abs_offset()[0] + self._scrollbar_pos,
                    rect.bottom
                    - surface.get_abs_offset()[1]
                    - self._style.scrollbar_size,
                ),
                (self._scrollbar_size, self._style.scrollbar_size),
                alpha,
                material_index=1,
            )

    def _update(self) -> None:
        if not self._element:
            return

        self._scrollbar_calc()
        element_w = self._element.get_abs_w(self.rect.w)
        max_scroll = element_w - self.rect.w + self.over_scroll[1]

        # Move the scrollbar if it's grabbed
        if self.scrollbar_grabbed:
            val = (_c.mouse_pos[0] - self.rect.x - self._scrollbar_grabbed_pos) / (
                self.rect.w - self._scrollbar_size
            ) * (max_scroll + self.over_scroll[0]) - self.over_scroll[0]

            self._scroll.val = val
            log.size.info("Scrollbar is grabbed, starting chain down...", self)
            self._update_element_rect()

        if not self.can_scroll:
            max_scroll = 0

        self._clamp_scroll_position(max_scroll)

        # Update the element
        self._element.update()

        if self._scroll.tick():
            log.size.info("Scroll is playing, starting chain down...", self)
            self._update_element_rect()

    def _update_element_rect(self) -> None:
        if self._element:
            with log.size.indent():
                padding = self._style.padding if self.can_scroll else 0

                if self.can_scroll:
                    element_x = self.rect.x - self._scroll.val
                    element_w = self.rect.w
                else:
                    element_x_obj = (
                        self._element._x
                        if self._element._x is not None
                        else self.content_x
                    )
                    element_w = self.rect.w - abs(element_x_obj.value)

                    element_x = self.rect.x + element_x_obj.get(self.rect.w, self._element.get_abs_w(element_w)
                    )

                element_y_obj = (
                    self._element._y if self._element._y is not None else self.content_y
                )
                element_y = self.rect.y + element_y_obj.get(
                    self.rect.h - padding,
                    self._element.get_abs_h(
                        self.rect.h - abs(element_y_obj.value) - padding
                    ),
                )

                self._element.set_active_w(self.content_w)
                self._element.set_active_h(self.content_h)

                self._element._update_rect(
                    self._subsurf,
                    element_x,
                    element_y,
                    self._element.get_abs_w(element_w),
                    self._element.get_abs_h(self.rect.h - padding - abs(element_y_obj.value)),
                )

    def _event2(self, event: pygame.event.Event) -> bool:
        if self.scrollbar_hovered:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.scrollbar_grabbed = True
                self._scrollbar_grabbed_pos = _c.mouse_pos[0] - (
                    self.rect.x + self._scrollbar_pos
                )
                return True

        if event.type == pygame.MOUSEWHEEL and self.can_scroll:
            if self.rect.collidepoint(_c.mouse_pos):
                change = -event.x if event.x else event.y
                self._scroll.val = pygame.math.clamp(
                    self._scroll.val - change * self._style.scroll_speed,
                    -self.over_scroll[0],
                    self._element.rect.w - self.rect.w + self.over_scroll[1],
                )
                log.size.info("Scrollwheel moved, starting chain down...", self)
                self._update_element_rect()
                self._scrollbar_calc()
                return True
        return False

    def _scrollbar_calc(self) -> None:
        element_w = self._element.get_abs_w(self.rect.w)
        max_scroll = element_w - self.rect.w + self.over_scroll[1]

        old_can_scroll = self.can_scroll

        # Scrollbar position and size calculations
        if not element_w:
            log.size.info("Scrollbar disabled", self)
            self.can_scroll = False

        else:
            self._scrollbar_size = (
                self.rect.w
                / max(1.0, (element_w + self.over_scroll[0] + self.over_scroll[1]))
            ) * self.rect.w
            self.can_scroll = self._scrollbar_size < self.rect.w
            if old_can_scroll != self.can_scroll:
                log.size.info(
                    f"Scrollbar {'enabled' if self.can_scroll else 'disabled'}, starting chain down...", self
                )
                self._update_element_rect()

            if self.can_scroll:
                self._scrollbar_pos = (
                    (self._scroll.val + self.over_scroll[0])
                    / (max_scroll + self.over_scroll[0])
                ) * (self.rect.w - self._scrollbar_size)

                rect = pygame.Rect(
                    self.rect.x + self._scrollbar_pos,
                    self.rect.bottom - self._style.scrollbar_size,
                    self._scrollbar_size,
                    self._style.scrollbar_size,
                )
                self.scrollbar_hovered = rect.collidepoint(_c.mouse_pos)

        self._clamp_scroll_position(max_scroll)

    def scroll_to_show_position(
        self, position: int, size: int = 0, offset: int = 0, duration: float = 0.1
    ) -> None:
        if not self.can_scroll:
            if self._scroll.val != (val := self.over_scroll[0] * -1):
                self._scroll.val = val
                log.size.line_break()
                with log.size.indent(f"Attempted scroll to show position, but cannot scroll. "
                    f"Set scroll val to {val}. Starting chain down...", self):
                    self._update_element_rect()
            return
        if position - offset <= self.rect.x:
            position -= offset
            destination = self._scroll.val - (self.rect.x - position)
        elif position + size + offset > self.rect.right:
            position += offset
            destination = (
                    self._scroll.val - (self.rect.x - position) - self.rect.w + size
            )
        else:
            return

        log.size.info(f"Scrolling to position {position}.", self)

        destination = pygame.math.clamp(
            destination,
            -self.over_scroll[0],
            self._element.get_abs_w(self.rect.w)
            - self.rect.w
            + self.over_scroll[1],
        )
        if self._scroll.play(stop=destination, duration=duration):
            self._update_element_rect()
        self._scrollbar_calc()

    def scroll_to_element(self, element: Element) -> None:
        if not self.rect.contains(element.rect):
            log.size.info(f"Scrolling so that {element} is visible.", self)
            self.scroll_to_show_position(element.rect.x, element.rect.w)
