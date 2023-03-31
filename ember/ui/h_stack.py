import pygame
import logging
import math
from typing import Union, Literal

import ember
from ember import common as _c
from ember.ui.element import Element
from ember.ui.stack import Layout
from ember.size import Size, FIT, FILL
from ember.ui.view import View


class HStack(Layout):
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
                 align_elements: Literal["top", "center", "bottom"] = "center"
                 ):

        self.background = background

        self.spacing = spacing
        self.min_spacing = min_spacing if spacing is None else spacing
        self.self_selectable = self_selectable
        self.selection_on_entry = selection_on_entry
        self.align_elements = align_elements

        super().__init__(*self._calculate_size(elements, size, width, height))
        self.set_elements(*elements)

    def calc_fit_size(self):
        if self.width.mode == 1:
            if self._elements:
                total_width = 0
                for i in self.elements:
                    if i.width.mode == 2:
                        raise ValueError("Cannot have elements of FILL width inside of a FIT width HStack.")
                    total_width += i.get_width(0)
                self._fit_width = total_width + self.min_spacing * (len(self._elements) - 1)
            else:
                self._fit_width = 20

        if self.height.mode == 1:
            if self._elements:
                if any(i.height.mode == 2 for i in self._elements):
                    raise ValueError("Cannot have elements of FILL height inside of a FIT height HStack.")
                self._fit_height = max(i.get_height(0) for i in self._elements)
            else:
                self._fit_height = 20

        self.selectable = any(i.selectable for i in self._elements)
        if hasattr(self.parent, "calc_fit_size"):
            self.parent.calc_fit_size()

    def _get_width_of_elements(self, my_width: int, use_min_spacing: bool = False):
        return total_width, remaining_width, spacing, element_fit_total

    def update_rect(self, pos, max_size, root: "View",
                    _ignore_fill_width: bool = False, _ignore_fill_height: bool = False):

        # Calculate own width
        stack_width = self.get_width(max_size[0])
        padding = self.width.value if self.width.mode == 1 else 0

        # Calculate the total width of the elements, and the spacing between them
        width_of_elements = 0
        element_fill_width = 0
        for i in self._elements:
            if i.width.mode == 2:
                element_fill_width += i.width.percentage
            else:
                width_of_elements += i.get_width(0)

        if self.spacing is not None:
            spacing = self.spacing

        elif element_fill_width == 0:
            if len(self._elements) == 1:
                spacing = 0
            else:
                spacing = max(self.min_spacing, (stack_width - padding - width_of_elements) / (len(self._elements) - 1))
        else:
            spacing = self.min_spacing

        remaining_width = round(stack_width) - padding - width_of_elements - spacing * (len(self._elements) - 1)

        # Update own width and height
        stack_height = self.get_height(max_size[1])

        self.rect.update(*pos, stack_width, stack_height)

        # Update width and height of elements
        if not self._elements:
            return

        if element_fill_width == 0 and (self.spacing is not None or len(self._elements) == 1):
            x = remaining_width / 2 + padding / 2
        else:
            x = padding / 2

        self._first_visible_element = None
        for n,element in enumerate(self._elements):
            if self.align_elements == "center":
                y = pos[1] + self.rect.h / 2 - element.get_height(stack_height) / 2
            elif self.align_elements == "top":
                y = pos[1] + 0
            else:
                y = pos[1] + stack_height - element.get_height(self.rect.h)

            if element.width.mode == 2:
                w = remaining_width / element_fill_width * element.width.percentage
            else:
                w = element.get_width(0)

            element.update_rect((pos[0] + x, y),
                                max_size=(w, self.rect.h),
                                root=root, _ignore_fill_width=True)

            if x+w < self.parent.rect.left - self.rect.left or x > self.parent.rect.right - self.rect.left:
                element.visible = False
            else:
                element.visible = True
                if self._first_visible_element is None:
                    self._first_visible_element = n

            x += spacing + w

    def focus(self, root: View, previous=None, key: str = 'select'):
        logging.debug(f"Selected HStack")

        looking_for = root.element_focused if previous is None else previous

        if key in {'left', 'right', 'forward', 'backward'}:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = len(self._elements) - 1 if key == 'left' else 0
                
            if key in {'left','backward'}:
                end = 0
                amount = -1
            else:
                end = len(self._elements) - 1
                amount = 1

            # Find an element that we can select
            while index != end:
                index += amount
                if self._elements[index].selectable:
                    logging.debug(f"-> child")
                    return self._elements[index].focus(root, None)

            # If no element is found, return to the parent
            logging.debug(f"-> parent")
            return self.parent.focus(root, self, key=key)

        elif key in {'up', 'down'}:
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
                logging.debug(f"HStack has no selectable elements")
                return None
        else:
            logging.debug(f"Entering first element")
            for element in self._elements:
                if element.selectable:
                    closest_element = element
                    break
            else:
                logging.debug(f"HStack has no selectable elements")
                return None
        return closest_element.focus(root, None, key=key)
