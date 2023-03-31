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

from ember.utility.timer import BasicTimer
from ember.utility.load_ui_element import load_element


class SelectableStack:
    def __init__(self):
        pass
    
    def set_elements(self, *elements):
        self._elements = [None] * len(elements)
        for n, i in enumerate(elements):
            i = load_element(i, default_text_style=self.style.default_text_height)
            self._elements[n] = i

            if isinstance(i, Interactive):
                raise ValueError("Selectable Stack element cannot contain interactive elements.")
            i.selectable = True if not i.disabled else False
            if isinstance(i, Layout):
                i.self_selectable = True
        self._update_elements()

    def append(self, element):
        element = load_element(element, default_text_style=self.style.default_text_height)

        if isinstance(element, Interactive):
            raise ValueError("Selectable Stack element cannot contain interactive elements.")

        element.selectable = True if not i.disabled else False
        if isinstance(element, Layout):
            element.self_selectable = True

        self._elements.append(element)
        self._update_elements()

    def update(self, root: View):

        if not self._elements:
            return

        if root.element_focused in self.elements:
            if self.row_selected is not root.element_focused:
                self.set_selected(root.element_focused)

        self.sel_pos_anim.tick()
        self.sel_size_anim.tick()

        [i.update_a(root) for i in self._elements]
        
    def _enter_in_first_element(self, root, key):
        if self.self_selectable:
            return self

        if self.row_selected:
            return self.row_selected.focus(root, None, key=key)
