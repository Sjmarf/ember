import pygame
import logging
from typing import Union, Optional, NoReturn, Literal


from .element import Element
from .view import View
from .resizable import Resizable
from ..material.material import MaterialController

from ..size import Size, FIT, FILL


class Box(Element, Resizable):
    def __init__(self,
                 element: Optional[Element],
                 size: Union[tuple[Union[Size, int], Union[Size, int]], None] = None,
                 width: Union[float, None] = None,
                 height: Union[float, None] = None,
                 background=None,
                 can_focus_self: bool = False,
                 resizable_side: Union[list[Literal["left", "right", "top", "bottom"]],
                                       Literal["left", "right", "top", "bottom"], None] = None,
                 resize_limits: tuple[int, int] = (50, 300)
                 ):

        super().__init__(size, width, height,
                         default_size=(FIT if not element or element._width.mode != 2 else FILL,
                                       FIT if not element or element._height.mode != 2 else FILL))

        self.background = background
        self.material_controller = MaterialController(self)
        self.material_controller.set_material(self.background)

        self.can_focus_self = can_focus_self
        self.resizable_side = (resizable_side) if type(resizable_side) is str else resizable_side
        self.resize_limits = resize_limits

        self._fit_width = 0
        self._fit_height = 0

        self._hovering_resize_edge = None
        self._resizing = None
        self.set_element(element)

    def __repr__(self):
        return "<Box>"

    def set_element(self, element):
        self._element = element
        self._update_rect_chain_up()
        if element is not None:
            self.selectable = element._can_focus
            self._element._set_parent(self)
        else:
            self.selectable = False

    def _update_rect_chain_up(self):
        if self._height.mode == 1:
            if self._element:
                self._fit_height = self._element.get_abs_height(0)
            else:
                self._fit_height = 20

        if self._width.mode == 1:
            if self._element:
                self._fit_width = self._element.get_abs_width(0)
            else:
                self._fit_width = 20

        if self.parent:
            self.parent._update_rect_chain_up()
            self.root.check_size = True

    def _set_root(self, root):
        self.root = root
        if self._element:
            self._element._set_root(root)

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                root: "View", _ignore_fill_width: bool = False,
                                _ignore_fill_height: bool = False) -> NoReturn:

        super()._update_rect_chain_down(surface, pos, max_size, root, _ignore_fill_width, _ignore_fill_height)

        if self._element:
            self._element._update_rect_chain_down(
                surface,
                (pos[0] + self.get_abs_width(max_size[0]) / 2 - self._element.get_abs_width(self.rect.w) / 2,
                 pos[1] + self.get_abs_height(max_size[1]) / 2 - self._element.get_abs_height(self.rect.h) / 2),
                self.rect.size, root)

    def _update(self, root: View):
        if self._element:
            self._element._update_a(root)

        if self.resizable_side and not self._resizing:
            self._is_hovering_resizable_edge()

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255):
        rect = self.rect.move(*offset)

        if self.background:
            self.material_controller.render(self, surface,
                                            (rect.x - surface.get_abs_offset()[0],
                                             rect.y - surface.get_abs_offset()[1]),
                                            rect.size, alpha)

        if self._element:
            self._element._render_a(surface, offset, root, alpha=alpha)

    def _event(self, event: int, root: View):
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
            self._element._event(event, root)

    def _focus_chain(self, root: View, previous=None, direction: str = 'in'):
        logging.debug(f"Selected Box")
        if self.can_focus_self:
            return self

        if direction in {'up', 'down', 'left', 'right', 'forward', 'out'} or self._element is None:
            logging.debug(f"Exiting Box")
            return self.parent._focus_chain(root, self, direction=direction)
        else:
            return self._element._focus_chain(root, None, direction=direction)

    def _get_element(self):
        return self._element

    element = property(
        fget=_get_element
    )
