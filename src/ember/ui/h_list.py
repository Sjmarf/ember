import pygame
from typing import Union, Optional, Sequence, NoReturn
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


from .. import common as _c
from .h_stack import HStack
from .view import View

from ..size import SizeType, SequenceSizeType
from ..common import INHERIT, InheritType

from .element import Element
from .list import List

from ..style.list_style import ListStyle
from ..style.stack_style import StackStyle

from ..material.material import MaterialController, Material
from ..transition.transition import Transition

from .ui_object import Interactive
from .stack import Stack
from . import load_element


class HList(List, HStack):
    def __init__(self,
                 # Stack parameters
                 *elements: Union[str, Element],
                 size: SequenceSizeType = None,
                 width: SizeType = None,
                 height: SizeType = None,

                 style: Union[StackStyle, ListStyle, None] = None,
                 stack_style: Optional[StackStyle] = None,
                 list_style: Optional[ListStyle] = None,

                 background: Material = None,
                 spacing: Union[InheritType, int] = INHERIT,
                 min_spacing: Union[InheritType, int] = INHERIT,
                 focus_self: Union[InheritType, bool] = INHERIT,
                 align_elements: Union[InheritType, Literal["top", "center", "bottom"]] = INHERIT,

                 # Exclusive to Selectable Stack
                 selected: Optional[Element] = None,
                 highlight_overdraw: tuple[int, int] = (0, 0)
                 ):

        if isinstance(style, ListStyle):
            list_style = style
        elif isinstance(style, StackStyle):
            stack_style = style

        List.__init__(self, list_style, selected)

        HStack.__init__(self, *elements, size=size, width=width, height=height, background=background,
                        spacing=spacing, min_spacing=min_spacing, focus_self=focus_self,
                        align_elements=align_elements, style=
                        stack_style if stack_style else self._list_style.stack_style)

        self.highlight_overdraw = highlight_overdraw

        self.highlight_material_controller: MaterialController = MaterialController(self)

    def __repr__(self):
        return f"<HList({len(self._elements)} elements)>"

    def set_selected(self, element: Union[int,Element]) -> NoReturn:
        if isinstance(element, int):
            element = self._elements[element]
        if self.root.element_focused is self.selected:
            self.root.element_focused = element
        self.selected = element
        self.sel_pos_anim.play(stop=element.rect.x - self.rect.x, duration=0.1)
        self.sel_size_anim.play(stop=element.rect.width, duration=0.1)
        event = pygame.event.Event(ember.event.LISTITEMSELECTED, element=self, item=self.selected,
                                   index=self._elements.index(self.selected))
        pygame.event.post(event)

    def _update_elements(self, animation: Optional[Transition] = None,
                         old_elements: Sequence[Element] = None) -> NoReturn:
        super()._update_elements(animation, old_elements)
        if self.selected is None:
            if self._elements:
                self.selected = self._elements[0]
                self.sel_pos_anim.val = 0
                self.sel_size_anim.val = self.selected.get_abs_width(0)

    def _load_element(self, element: Union[str, Element]) -> Element:
        element = load_element(element, text_width=self._list_style.text_width)

        if isinstance(element, Interactive):
            raise ValueError("Selectable Stack element cannot contain interactive elements.")
        element._can_focus = True if not element.disabled else False
        if isinstance(element, Stack):
            element.focus_self = True
        element._set_parent(self)
        return element

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                root: "View", _ignore_fill_width: bool = False,
                                _ignore_fill_height: bool = False) -> NoReturn:

        HStack._update_rect_chain_down(self, surface, pos, max_size, root, _ignore_fill_width, _ignore_fill_height)
        if self._defer_selection and self.selected is not None:
            self.sel_pos_anim.val = self.selected.rect.x - self.rect.x
            self.sel_size_anim.val = self.selected.rect.w
            self._defer_selection = False

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], root: View, alpha: int = 255):

        rect = self.rect.move(*offset)
        self._render_background(surface, offset, root, alpha)

        material = self._list_style.highlight_focus_material if \
            root.element_focused is self.selected else self._list_style.highlight_material
        self.highlight_material_controller.set_material(material, self._list_style.material_transition)
        if material:
            self.highlight_material_controller.render(self, surface,
                                                      (rect.x - surface.get_abs_offset()[0] +
                                                       self.sel_pos_anim.val - self.highlight_overdraw[0],
                                                       rect.y - surface.get_abs_offset()[1]),
                                                      (self.sel_size_anim.val + sum(self.highlight_overdraw), rect.h),
                                                      alpha)

        self._render_elements(surface, offset, root, alpha)

    def _event(self, event, root):
        if HStack._event(self, event, root):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(_c.mouse_pos):
                for element in self._elements:
                    if element.rect.collidepoint((_c.mouse_pos[0], element.rect.y)):
                        if not (hasattr(element, 'disabled') and element.disabled):
                            self.set_selected(element)
                            if root.element_focused in self.elements:
                                root.element_focused = element
