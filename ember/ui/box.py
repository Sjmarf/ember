import pygame
import logging
from typing import Union, Literal, Optional

from ember import common as _c
from ember.ui.element import Element
from ember.ui.view import View
from ember.ui.resizable import Resizable
from ember.material.material import MaterialController

from ember.size import Size, FIT


class Box(Element, Resizable):
    def __init__(self,
                 element: Optional[Element],
                 size: Union[tuple[Union[Size, int], Union[Size, int]], None] = None,
                 width: Union[float, None] = None,
                 height: Union[float, None] = None,
                 background=None,
                 self_selectable: bool = False,
                 resizable_side: Union[list[Literal["left", "right", "top", "bottom"]],
                                       Literal["left", "right", "top", "bottom"], None] = None,
                 resize_limits: tuple[int, int] = (50, 300)
                 ):

        if size is None and width is None:
            width = FIT if not element or element.width.mode != 2 else FILL
        if size is None and height is None:
            height = FIT if not element or element.height.mode != 2 else FILL

        width = size[0] if width is None else width
        height = size[1] if height is None else height
        super().__init__(width, height)

        self.background = background
        self.material_controller = MaterialController(self)
        self.material_controller.set_material(self.background)

        self.self_selectable = self_selectable
        self.resizable_side = (resizable_side) if type(resizable_side) is str else resizable_side
        self.resize_limits = resize_limits

        self._fit_width = 0
        self._fit_height = 0

        self._hovering_resize_edge = None
        self._resizing = None
        self.set_element(element)

    def set_element(self, element):
        self._element = element
        self.calc_fit_size()
        if element is not None:
            self.selectable = element.selectable
            self._element.set_parent(self)
        else:
            self.selectable = False

    def calc_fit_size(self):
        if self.height.mode == 1:
            if self._element:
                self._fit_height = self._element.get_height(0)
            else:
                self._fit_height = 20

        if self.width.mode == 1:
            if self._element:
                self._fit_width = self._element.get_width(0)
            else:
                self._fit_width = 20

        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()

    def set_root(self, root):
        self.root = root
        if self._element:
            self._element.set_root(root)

    def update_rect(self, pos, max_size, root: "View",
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        super().update_rect(pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

        if self._element:
            self._element.update_rect(
                (pos[0] + self.get_width(max_size[0]) / 2 - self._element.get_width(self.rect.w) / 2,
                 pos[1] + self.get_height(max_size[1]) / 2 - self._element.get_height(self.rect.h) / 2),
                self.rect.size, root)

    def update(self, root: View):
        if self._element:
            self._element.update_a(root)

        if self.resizable_side and not self._resizing:
            self._is_hovering_resizable_edge()

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255):
        rect = self.rect.move(*offset)

        if self.background:
            self.material_controller.render(self, surface,
                                            (rect.x - surface.get_abs_offset()[0],
                                             rect.y - surface.get_abs_offset()[1]),
                                            rect.size, alpha)

        if self._element:
            self._element.render_a(surface, offset, root, alpha=alpha)

    def event(self, event: int, root: View):
        if self._hovering_resize_edge:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._resizing = True
                return

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._resizing = False
                return

            elif event.type == pygame.MOUSEMOTION and self._resizing:
                self._resize()

        if self._element is not None:
            self._element.event(event, root)

    def focus(self, root: View, previous=None, key: str = 'select'):
        logging.debug(f"Selected Box")
        if self.self_selectable:
            return self

        if key in {'up', 'down', 'left', 'right', 'forward'} or self._element is None:
            logging.debug(f"Exiting Box")
            return self.parent.focus(root, self, key=key)
        else:
            return self._element.focus(root, None, key=key)

    def _get_element(self):
        return self._element

    element = property(
        fget=_get_element
    )
