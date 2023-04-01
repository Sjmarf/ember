import math
import logging
from typing import Union, Literal, Optional

import ember
from ember import common as _c
from ember.ui.element import Element
from ember.ui.stack import Layout
from ember.ui.view import View

from ember.size import Size

class HGrid(Layout):
    def __init__(self,
                 *elements: Element,
                 size: Union[tuple[Union[Size, int], Union[Size, int]], None] = None,
                 width: Union[Size, int, None] = None,
                 height: Union[Size, int, None] = None,
                 element_size: Optional[tuple[int,int]] = None,
                 background=None,
                 spacing: int = 6,
                 selection_on_entry: Literal['closest', 'first'] = 'closest',
                 self_selectable: bool = False,
                 align_elements: Literal["top", "center", "bottom"] = "center"
                 ):

        self.background = background
        
        self.element_size = element_size

        self._items_per_row = None
        self.spacing = spacing
        self.self_selectable = self_selectable
        self.selection_on_entry = selection_on_entry
        self.align_elements = align_elements

        super().__init__(*self._calculate_size(elements, size, width, height))
        self.set_elements(*elements)
        
    def set_elements(self, *elements):
        if self.element_size is not None:
            pass
        elif elements and elements[0].width.mode != 2 and elements[0].height.mode != 2:
            self.element_size = (elements[0].get_width(0),elements[0].get_height(0))
        else:
            self.element_size = None
            
        self._elements = list(elements)
        self._update_elements()

    def calc_fit_size(self):
        if self.width.mode == 1:
            if self._elements:
                self._fit_width = self.element_size[0]*len(self._elements) + self.spacing * (len(self._elements)-1)
            else:
                self._fit_width = 20

        if self.height.mode == 1:
            if self._elements:
                if self._items_per_row is None:
                    self._fit_height = 20
                    return
                row_count = math.ceil(len(self._elements)/self._items_per_row) 
                self._fit_height = row_count*self.element_size[1]+(row_count-1)*self.spacing
            else:
                self._fit_height = 20

        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()

    def update_rect(self, pos, max_size, root: "View",
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        # Calculate own width
        stack_width = self.get_width(max_size[0])
        stack_height = self.get_height(max_size[1])

        self.rect.update(*pos, stack_width, stack_height)

        # Update width and height of elements
        if not self._elements:
            return

        items_per_row = (stack_width-self.spacing) // (self.element_size[0]+self.spacing)
        if items_per_row != self._items_per_row:
            self._items_per_row = items_per_row
            self.calc_fit_size()

        content_width = self._items_per_row*self.element_size[0]+(self._items_per_row-1)*self.spacing
        start_x = (stack_width-content_width)/2

        n = 0
        x = start_x
        y = 0

        for element in self._elements:
            element.update_rect((pos[0] + x, pos[1] + y),
                                max_size=self.element_size,
                                root=root, _ignore_fill_width=True)

            x += self.element_size[0] + self.spacing
            n += 1
            if n >= self._items_per_row:
                n = 0
                y += self.element_size[1] + self.spacing
                x = start_x

    def focus(self, root: View, previous=None, key: str = 'select'):
        logging.debug(f"Selected HGrid")

        looking_for = root.element_focused if previous is None else previous

        if key in {'left', 'right'}:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = len(self._elements) - 1 if key == 'left' else 0
            end = (self._items_per_row*(index//self._items_per_row))
            if key == 'right':
                end += self._items_per_row - 1
            amount = -1 if key == 'left' else 1

            # Find an element that we can select
            while index != end:
                index += amount
                if index > len(self._elements) - 1:
                    break
                if self._elements[index].selectable:
                    logging.debug(f"-> child")
                    return self._elements[index].focus(root, None)

            # If no element is found, return to the parent
            logging.debug(f"-> parent")
            return self.parent.focus(root, self, key=key)

        elif key in {'up', 'down'}:
            index = self._elements.index(looking_for)
            if key == 'up' and index < self._items_per_row:
                logging.debug(f"-> parent")
                return self.parent.focus(root, self, key=key)

            if key == 'down' and index > len(self._elements) - self._items_per_row:
                logging.debug(f"-> parent")
                return self.parent.focus(root, self, key=key)

            end = index % self._items_per_row if key == 'up' else len(self._elements) - (index % self._items_per_row)
            while index != end:
                amount = self._items_per_row * -1 if key == 'up' else self._items_per_row
                index += amount
                if index > len(self._elements)-1:
                    break
                if self._elements[index].selectable:
                    logging.debug(f"-> child")
                    return self._elements[index].focus(root, None)

            logging.debug(f"-> parent")
            return self.parent.focus(root, self, key=key)

        else:
            return self._enter_in_first_element(root, key)

    def _enter_in_first_element(self, root, key):
        # The stack is being entered, so select the element closest to the previous element
        if self.self_selectable:
            return self

        if root.element_focused is not None and self.selection_on_entry == 'closest':
            logging.debug(f"Entering in closest")
            closest_elements = sorted(self._elements,
                                      key=lambda x: abs(x.rect.centerx - root.element_focused.rect.centerx))
            for element in closest_elements:
                if element.selectable:
                    closest_element = element
                    break
            else:
                logging.debug(f"HGrid has no selectable elements")
                return None
        else:
            logging.debug(f"Entering first element")
            for element in self._elements:
                if element.selectable:
                    closest_element = element
                    break
            else:
                logging.debug(f"HGrid has no selectable elements")
                return None
        return closest_element.focus(root, None, key=key)
