import pygame
from typing import TYPE_CHECKING, Optional, Sequence, NoReturn, Union

if TYPE_CHECKING:
    from ember.ui.view import View

from ember.common import INHERIT, InheritType

from ember import log
from ember import common as _c
from ember.ui.element import Element
from ember.material.material import MaterialController, Material
from ember.size import FIT, SizeType

from ember.style.scroll_style import ScrollStyle
from ember.ui.scroll import Scroll


class HScroll(Scroll):
    def __init__(self,
                 element: Optional[Element],
                 size: Sequence[SizeType] = (0, 0),
                 width: SizeType = None,
                 height: SizeType = None,

                 style: Optional[ScrollStyle] = None,

                 background: Optional[Material] = None,
                 focus_self: bool = False,
                 over_scroll: Union[InheritType, Sequence[int]] = INHERIT
                 ):

        super().__init__(element, size, width, height, style, background, focus_self, over_scroll)

    def __repr__(self):
        return "<HScroll>"

    def _update_element_rect(self):
        if self._element:
            with log.size.indent:
                padding = (self._style.padding if self.can_scroll else 0)
                self._element._update_rect_chain_down(self.subsurf, (self.rect.x - self.scroll.val,
                                                                     self.rect.y + (self.rect.h-padding) // 2 -
                                                                     self._element.get_abs_height(self.rect.h-padding)
                                                                     // 2),
                                                      (self.rect.h - padding,
                                                      self.rect.w), self.root)

    def _update(self, root: "View") -> NoReturn:

        if not self._element:
            return

        self._scrollbar_calc()
        element_w = self._element.get_abs_width(self.rect.w)
        max_scroll = element_w - self.rect.w + self.over_scroll[1]

        # Move the scrollbar if it's grabbed
        if self.scrollbar_grabbed:
            val = (_c.mouse_pos[0] - self.rect.x - self._scrollbar_grabbed_pos) / \
                  (self.rect.w - self._scrollbar_size) * (max_scroll + self.over_scroll[0]) - self.over_scroll[0]

            self.scroll.val = val
            log.size.info(self, "Scrollbar is grabbed, starting chain down...")
            self._update_element_rect()

        if not self.can_scroll:
            max_scroll = 0

        self._clamp_scroll_position(max_scroll)

        # Update the element
        self._element._update_a(root)

        if self.scroll.tick():
            log.size.info(self, "Scroll is playing, starting chain down...")
            self._update_element_rect()

    def _scrollbar_calc(self):
        element_w = self._element.get_abs_width(self.rect.w)
        max_scroll = element_w - self.rect.w + self.over_scroll[1]

        old_can_scroll = self.can_scroll

        # Scrollbar position and size calculations
        if not element_w:
            self.can_scroll = False

        else:
            self._scrollbar_size = (self.rect.w / (element_w + self.over_scroll[0] + self.over_scroll[1])) * self.rect.w
            self.can_scroll = self._scrollbar_size < self.rect.w
            if old_can_scroll != self.can_scroll:
                log.size.info(self, f"Scrollbar {'enabled' if self.can_scroll else 'disabled'}, starting chain down...")
                self._update_element_rect()

            if self.can_scroll:
                self._scrollbar_pos = ((self.scroll.val + self.over_scroll[0]) / (max_scroll + self.over_scroll[0])) \
                                      * (self.rect.w - self._scrollbar_size)

                rect = pygame.Rect(self.rect.x + self._scrollbar_pos,
                                   self.rect.bottom - self._style.scrollbar_size,
                                   self._scrollbar_size, self._style.scrollbar_size)
                self.scrollbar_hovered = rect.collidepoint(_c.mouse_pos)

        self._clamp_scroll_position(max_scroll)

    def _render_scrollbar(self, surface: pygame.Surface, rect: pygame.Rect, alpha: int) -> NoReturn:
        max_scroll = self._element.rect.w - self.rect.w + self.over_scroll[1]
        self._clamp_scroll_position(max_scroll)

        # Draw scrollbar
        if self.can_scroll:
            self.base_controller.set_material(self._style.base_material)
            self.base_controller.render(self, surface, (rect.x, rect.y + rect.h - self._style.scrollbar_size),
                                        (rect.w, self._style.scrollbar_size), alpha)

            if self.scrollbar_grabbed:
                material = self._style.handle_click_material
            elif self.scrollbar_hovered:
                material = self._style.handle_hover_material
            else:
                material = self._style.handle_material
            self.handle_controller.set_material(material, self._style.handle_material_transition)
            self.handle_controller.render(self, surface,
                                          (rect.x + self._scrollbar_pos,
                                           rect.bottom - self._style.scrollbar_size),
                                          (self._scrollbar_size + 1, self._style.scrollbar_size),
                                          alpha)

    def _event2(self, event: pygame.event.Event, root: "View") -> NoReturn:
        if self.scrollbar_hovered:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.scrollbar_grabbed = True
                self._scrollbar_grabbed_pos = _c.mouse_pos[0] - (self.rect.x + self._scrollbar_pos)
                return True

        if event.type == pygame.MOUSEWHEEL and self.can_scroll:
            if self.rect.collidepoint(_c.mouse_pos):
                change = -event.x if event.x else event.y
                self.scroll.val = pygame.math.clamp(self.scroll.val - change * self._style.scroll_speed,
                                                    - self.over_scroll[0],
                                                    self._element.rect.w - self.rect.w + self.over_scroll[1])
                log.size.info(self, "Scrollwheel moved, starting chain down...")
                self._update_element_rect()

    def scroll_to_show_position(self, position: int, size: int = 0, offset: int = 0, duration: float = 0.1):
        if not self.can_scroll:
            self.scroll.val = 0
            self._update_element_rect()
            return
        if position - offset <= self.rect.x:
            position -= offset
            destination = self.scroll.val - (self.rect.x - position)
        elif position + size + offset > self.rect.right:
            position += offset
            destination = self.scroll.val - (self.rect.x - position) - self.rect.w + size
        else:
            return

        log.size.info(self, f"Scrolling to position {position}.")

        destination = pygame.math.clamp(destination,
                                        -self.over_scroll[0],
                                        self._element.get_abs_width(self.rect.w) - self.rect.w + self.over_scroll[1])
        if self.scroll.play(stop=destination, duration=duration):
            self._update_element_rect()
        self._scrollbar_calc()

    def scroll_to_element(self, element: Element) -> NoReturn:
        if not self.rect.contains(element.rect):
            log.size.info(self, f"Scrolling so that {element} is visible.")
            self.scroll_to_show_position(element.rect.x, element.rect.w)
