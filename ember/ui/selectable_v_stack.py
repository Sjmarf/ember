import pygame
from typing import Union, Literal, Optional

from ember import common as _c
from ember.ui.v_stack import VStack
from ember.ui.view import View

import ember
from ember.size import Size, FIT
from ember.ui.ui_object import Interactive
from ember.ui.element import Element
from ember.style.list_style import ListStyle
from ember.ui.stack import Layout
from ember.ui.selectable_stack import SelectableStack

from ember.utility.timer import BasicTimer
from ember.utility.load_ui_element import load_element

from ember.material.material import MaterialController


class SelectableVStack(SelectableStack, VStack):
    def __init__(self,
                 # Stack parameters
                 *elements: Union[Element, str],
                 size: Union[tuple[Union[Size, int], Union[Size, int]], None] = (FIT, FIT),
                 width: Union[Size, int, None] = None,
                 height: Union[Size, int, None] = None,
                 style: Optional[ListStyle] = None,
                 background=None,
                 spacing: Optional[int] = None,
                 min_spacing: int = 6,
                 self_selectable: bool = False,
                 align_elements: Literal["left", "center", "right"] = "center",

                 # Exclusive to Selectable Stack
                 row_selected: Optional[Element] = None,
                 selection_overdraw: tuple[int, int] = (0, 0)
                 ):

        # Load the ListStyle object.
        if style is None:
            if _c.default_list_style is None:
                logging.debug("Loading default ListStyle")
                _c.default_list_style = ListStyle()
            self.style = _c.default_list_style
        else:
            self.style = style

        elements = [load_element(i, default_text_style=self.style.default_text_height) for i in elements]
        if row_selected is None:
            if elements:
                self.row_selected = elements[0]
            else:
                self.row_selected = None
        else:
            self.row_selected = row_selected

        VStack.__init__(self, *elements, size=size, width=width, height=height, background=background,
                        spacing=spacing, min_spacing=min_spacing, self_selectable=self_selectable,
                        align_elements=align_elements)
        SelectableStack.__init__(self)

        self._defer_selection = True
        self.sel_pos_anim = BasicTimer(0)
        self.sel_size_anim = BasicTimer(0)

        self.selection_overdraw = selection_overdraw
        
        self.background_material_controller = MaterialController(self)
        self.highlight_material_controller = MaterialController(self)
        
        self.background_material_controller.set_material(self.background)        

    def set_selected(self, element: Element):
        self.row_selected = element
        self.sel_pos_anim.play(stop=element.rect.y - self.rect.y, duration=0.1)
        self.sel_size_anim.play(stop=element.rect.height, duration=0.1)
        event = pygame.event.Event(ember.event.LISTITEMSELECTED, element=self, item=self.row_selected,
                                   index=self._elements.index(self.row_selected))
        pygame.event.post(event)

    def _update_elements(self):
        super()._update_elements()
        if self.row_selected is None:
            if self._elements:
                self.row_selected = self._elements[0]
                self.sel_pos_anim.val = 0
                self.sel_size_anim.val = self.row_selected.get_height(0)

    def update_rect(self, pos, max_size, root: View,
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):
        VStack.update_rect(self, pos, max_size, root, _ignore_fill_width, _ignore_fill_height)
        if self._defer_selection and self.row_selected is not None:
            self.sel_pos_anim.val = self.row_selected.rect.y - self.rect.y
            self.sel_size_anim.val = self.row_selected.rect.h
            self._defer_selection = False

    def render(self, surface: pygame.Surface, offset: tuple[int, int], root: View,
               alpha: int = 255):

        rect = self.rect.move(*offset)

        if self.background:
            self.background_material_controller.render(self, surface, (rect.x - surface.get_abs_offset()[0],
                                                           rect.y - surface.get_abs_offset()[1]),
                                           rect.size)

        material = self.style.highlight_focus_material if \
            root.element_focused is self.row_selected else self.style.highlight_material
        self.highlight_material_controller.set_material(material)
        if material:
            self.highlight_material_controller.render(self, surface,
                            (rect.x - surface.get_abs_offset()[0],
                             rect.y - surface.get_abs_offset()[1] +
                             self.sel_pos_anim.val - self.selection_overdraw[0]),
                            (rect.w, self.sel_size_anim.val + sum(self.selection_overdraw)),
                            alpha)

        [i.render_a(surface, offset, root, alpha=alpha) for i in self.elements]

    def event(self, event, root):
        [i.event(event, root) for i in self._elements]
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(_c.mouse_pos):
                for element in self._elements:
                    if element.rect.collidepoint((element.rect.x, _c.mouse_pos[1])):
                        if not (hasattr(element, 'disabled') and element.disabled):
                            self.set_selected(element)
                            if root.element_focused in self.elements:
                                root.element_focused = element
