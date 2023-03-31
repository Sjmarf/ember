import pygame
import logging
from typing import Union, Literal, Optional

import ember
from ember import common as _c
from ember.ui.stack import Layout
from ember.size import Size, FIT, FILL
from ember.ui.view import View
from ember.ui.element import Element


class VStack(Layout):
    def __init__(self,
                 *elements: Element,
                 size: Union[tuple[Union[Size, int], Union[Size, int]], None] = None,
                 width: Union[Size, int, None] = None,
                 height: Union[Size, int, None] = None,
                 background=None,
                 spacing: Union[int, None] = None,
                 min_spacing: int = 6,
                 selection_on_entry: Literal['closest', 'first'] = 'closest',
                 self_selectable: bool = False,
                 align_elements: Literal["left", "center", "right"] = "center"):

        self.background = background

        self.spacing = spacing
        self.min_spacing = min_spacing if spacing is None else spacing
        self.self_selectable = self_selectable
        self.selection_on_entry = selection_on_entry
        self.align_elements = align_elements

        super().__init__(*self._calculate_size(elements, size, width, height))

        self.set_elements(*elements)

    def __repr__(self):
        return f"VStack({len(self._elements)} elements)"

    def calc_fit_size(self):
        if self.height.mode == 1:
            if self._elements:
                total_height = 0
                for i in self.elements:
                    if i.height.mode == 2:
                        raise ValueError("Cannot have elements of FILL height inside of a FIT height VStack.")
                    total_height += i.get_height(0)
                self._fit_height = total_height + self.min_spacing * (len(self._elements) - 1)
            else:
                self._fit_height = 20

        if self.width.mode == 1:
            if self._elements:
                if any(i.width.mode == 2 for i in self._elements):
                    raise ValueError("Cannot have elements of FILL width inside of a FIT width VStack.")
                self._fit_width = max(i.get_width(0) for i in self._elements)
            else:
                self._fit_width = 20

        self.selectable = any(i.selectable for i in self._elements)
        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()

    def update_rect(self, pos, max_size, root: "View",
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        # Calculate own height
        stack_height = self.get_height(max_size[1])
        padding = self.height.value if self.height.mode == 1 else 0

        # Calculate the total height of the elements, and the spacing between them
        height_of_elements = 0
        element_fill_height = 0
        for i in self._elements:
            if i.height.mode == 2:
                element_fill_height += i.height.percentage
            else:
                height_of_elements += i.get_height(0)

        if self.spacing is not None:
            spacing = self.spacing

        elif element_fill_height == 0:
            if len(self._elements) == 1:
                spacing = 0
            else:
                spacing = max(self.min_spacing, int((stack_height - padding - height_of_elements)
                                                    // (len(self._elements) - 1)))
        else:
            spacing = self.min_spacing

        remaining_height = stack_height - padding - height_of_elements - spacing * (len(self._elements) - 1)

        # Update own width and height
        stack_width = self.get_width(max_size[0])

        super().update_rect(pos, max_size, root)

        # Update width and height of elements
        if not self._elements:
            return

        if element_fill_height == 0 and (self.spacing is not None or len(self._elements) == 1):
            y = remaining_height // 2 + padding / 2
        else:
            y = padding / 2

        self._first_visible_element = None
        for n,element in enumerate(self._elements):
            if self.align_elements == "center":
                x = pos[0] + stack_width / 2 - element.get_width(stack_width) / 2
            elif self.align_elements == "left":
                x = pos[0]
            else:
                x = pos[0] + stack_width - element.get_width(self.rect.w)

            if element.height.mode == 2:
                h = remaining_height / element_fill_height * element.height.percentage
            else:
                h = element.get_height(0)

            element.update_rect((x, pos[1] + y),
                                max_size=(self.rect.w, h),
                                root=root, _ignore_fill_height=True)

            if y+h < self.parent.rect.top - self.rect.top or y > self.parent.rect.bottom - self.rect.top:
                element.visible = False
            else:
                element.visible = True
                if self._first_visible_element is None:
                    self._first_visible_element = n

            y += spacing + h

    def focus(self, root: View, previous=None, key: str = 'select'):
        logging.debug(f"Selected {self} key '{key}'")

        looking_for = root.element_focused if previous is None else previous

        if key in {'up', 'down', 'forward', 'backward'}:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = len(self._elements) - 1 if key == 'up' else 0
                
            if key in {'up','backward'}:
                end = 0
                amount = -1
            else:
                end = len(self._elements) - 1
                amount = 1

            # Find an element that we can select
            while index != end:
                index += amount
                logging.debug(f"{self._elements[index]} {self._elements[index].selectable}")
                if self._elements[index].selectable:
                    logging.debug(f"-> child")
                    return self._elements[index].focus(root, None)

            # If no element is found, return to the parent
            logging.debug(f"-> parent")
            return self.parent.focus(root, self, key=key)

        elif key in {'left', 'right'}:
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
                                      key=lambda x: abs(x.rect.centery - root.element_focused.rect.centery))
            for element in closest_elements:
                if element.selectable:
                    closest_element = element
                    break
            else:
                logging.debug(f"VStack has no selectable elements")
                return None
        else:
            logging.debug(f"Entering first element")
            for element in self._elements:
                if element.selectable:
                    closest_element = element
                    break
            else:
                logging.debug(f"VStack has no selectable elements")
                return None
        return closest_element.focus(root, None, key=key)
