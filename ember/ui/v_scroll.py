import pygame
import logging
from typing import TYPE_CHECKING, Union, Literal, Optional

if TYPE_CHECKING:
    from ember.ui.view import View

from ember import common as _c
from ember.ui.element import Element
from ember.style.load_style import load as load_style
from ember.material.material import MaterialController

from ember.utility.timer import BasicTimer


class VScroll(Element):
    def __init__(self, element: Optional[Element], size: Union[tuple[float, float], None] = (0, 0),
                 width: Union[float, None] = None, height: Union[float, None] = None, style=None,
                 background=None, self_selectable: bool = False, over_scroll: tuple[int, int] = (0, 0)):

        width = size[0] if width is None else width
        height = size[1] if height is None else height
        super().__init__(width, height)

        # Load the ScrollStyle object.
        if style is None:
            if _c.default_scroll_style is None:
                load_style("plastic", parts=['scroll'])
            self.style = _c.default_scroll_style
        else:
            self.style = style

        self.subsurf = None

        self.background = background
        self.background_controller = MaterialController(self)
        self.background_controller.set_material(self.background)

        self.scroll_background_controller = MaterialController(self)
        self.scroll_handle_controller = MaterialController(self)

        self.self_selectable = self_selectable
        self.over_scroll = over_scroll

        self._fit_width = 0
        self._fit_height = 0

        self.set_element(element)

        self.scroll = BasicTimer(self.over_scroll[0] * -1)
        self.can_scroll = False
        self._scrollbar_y = 0
        self._scrollbar_h = 0
        self.scrollbar_hovered = False
        self.scrollbar_grabbed = False
        self._scrollbar_grabbed_y = 0

    def _get_element(self):
        return self._element

    def set_element(self, element):
        self._element = element
        if element is not None:
            self.selectable = element.selectable
            self._element.set_parent(self)
        else:
            self.selectable = False

    def calc_fit_size(self):
        if self.height.mode == 1:
            if self._element:
                if self._element.height.mode == 2:
                    raise ValueError("Cannot have elements of FILL height inside of a FIT height VScroll.")
                self._fit_height = self._element.get_height(0)
            else:
                self._fit_height = 20

        if self.width.mode == 1:
            if self._element:
                if self._element.width.mode == 2:
                    raise ValueError("Cannot have elements of FILL width inside of a FIT width VScroll.")
                self._fit_width = self._element.get_width(0)
            else:
                self._fit_width = 20

        if self._element:
            self.selectable = self._element.selectable
        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()

    def update_rect(self, pos, max_size, root: "View",
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        super().update_rect(pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

    def update(self, root: "View"):

        if not self._element:
            return

        if hasattr(self._element, "check_for_surface_update"):
            self._element.check_for_surface_update()

        # We use get_height for the element height because can_scroll needs to be used in the element update method
        element_h = self._element.get_height(self.rect.h)
        max_scroll = element_h - self.rect.h + self.over_scroll[1]

        # Scrollbar position and size calculations
        if not element_h:
            self.can_scroll = False

        else:
            self._scrollbar_h = (self.rect.h / (element_h + self.over_scroll[0] + self.over_scroll[1])) * self.rect.h
            self.can_scroll = self._scrollbar_h < self.rect.h

            if self.can_scroll:
                self._scrollbar_y = ((self.scroll.val + self.over_scroll[0]) / (max_scroll + self.over_scroll[0])) \
                                    * (self.rect.h - self._scrollbar_h)

                rect = pygame.Rect(self.rect.topright[0] - self.style.scrollbar_width, self.rect.y + self._scrollbar_y,
                                   self.style.scrollbar_width+1, self._scrollbar_h + 1)
                self.scrollbar_hovered = rect.collidepoint(_c.mouse_pos)

            # Move the scrollbar if it's grabbed
            if self.scrollbar_grabbed:
                val = (_c.mouse_pos[1] - self.rect.y - self._scrollbar_grabbed_y) / \
                      (self.rect.h - self._scrollbar_h) * (max_scroll + self.over_scroll[0]) - self.over_scroll[0]

                self.scroll.val = val

        # If the scrollbar is outside the limits, move it inside.
        if not (-self.over_scroll[0] <= self.scroll.val <= max_scroll):
            if self.can_scroll:
                self.scroll.val = min(max(-self.over_scroll[0], self.scroll.val), max_scroll)
            else:
                self.scroll.val = -self.over_scroll[0]

        # Update the element
        self._element.update_rect((self.rect.x + self.rect.w // 2 - self._element.get_width(self.rect.w) // 2,
                                   self.rect.y - self.scroll.val),
                                  (self.rect.w - (self.style.padding if self.can_scroll else 0),
                                   self.rect.h), root)
        self._element.update_a(root)

        self.scroll.tick()

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: "View", alpha: int = 255):
        rect = self.rect.move(*offset)

        if self.subsurf is None or (*self.subsurf.get_abs_offset(), *self.subsurf.get_size()) != self.rect:
            self.subsurf = surface.subsurface(self.rect)

        if self.background:
            self.background_controller.render(self, surface, (rect.x - surface.get_abs_offset()[0],
                                                              rect.y - surface.get_abs_offset()[1]),
                                              rect.size, alpha)

        if not self._element:
            return

        # Render element
        self._element.render_a(self.subsurf, offset, root, alpha=alpha)

        # Draw scrollbar
        if self.can_scroll:
            self.background_controller.set_material(self.style.images[0])
            self.background_controller.render(self, surface, (rect.x + rect.w - self.style.scrollbar_width, rect.y),
                                              (self.style.scrollbar_width, rect.h), alpha)

            img_num = 2 if self.scrollbar_hovered or self.scrollbar_grabbed else 1
            self.scroll_handle_controller.set_material(self.style.images[img_num])
            self.scroll_handle_controller.render(self, surface,
                                                 (rect.topright[0] - self.style.scrollbar_width,
                                                  rect.y + self._scrollbar_y),
                                                 (self.style.scrollbar_width, self._scrollbar_h + 1),
                                                 alpha)

    def event(self, event: int, root: "View"):
        if event.type == pygame.MOUSEWHEEL and self.can_scroll:
            if self.rect.collidepoint(_c.mouse_pos):
                self.scroll.val = min(max(-self.over_scroll[0], self.scroll.val - event.y * self.style.scroll_speed),
                                      self._element.rect.h - self.rect.h + self.over_scroll[1])

        if self.scrollbar_hovered:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.scrollbar_grabbed = True
                self._scrollbar_grabbed_y = _c.mouse_pos[1] - (self.rect.y + self._scrollbar_y)

        if event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_grabbed = False

        if self._element is not None:
            # Stops you from clicking on elements that are clipped out of the frame
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.rect.collidepoint(_c.mouse_pos):
                    return
            self._element.event(event, root)

    def focus(self, root: "View", previous=None, key: str = 'select'):
        logging.debug(f"Selected VScroll")
        if self.self_selectable:
            return self

        if key in {'up', 'down', 'left', 'right', 'forward'} or self._element is None:
            logging.debug(f"Exiting VScroll")
            return self.parent.focus(root, self, key=key)
        else:
            return self._element.focus(root, None, key=key)

    element = property(
        fget=_get_element,
        fset=set_element,
        doc="The element contained in the VScroll."
    )
