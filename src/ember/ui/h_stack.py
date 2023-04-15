import math
import pygame
from ..common import INHERIT, InheritType
from typing import Union, NoReturn, Optional, Sequence
try:
    from typing import Literal
except ModuleNotFoundError:
    from typing_extensions import Literal


from .stack import Stack
from .. import log
from ..size import FIT, FILL, SizeType, SequenceSizeType
from .view import View
from .element import Element
from ..material.material import Material

from ..style.stack_style import StackStyle

class HStack(Stack):
    def __init__(self,
                 *elements: Union[Element, Sequence[Element]],
                 size: SequenceSizeType = None,
                 width: SizeType = None,
                 height: SizeType = None,

                 style: Optional[StackStyle] = None,

                 background: Material = None,
                 spacing: Union[InheritType, int] = INHERIT,
                 min_spacing: Union[InheritType, int] = INHERIT,
                 focus_self: Union[InheritType, bool] = INHERIT,
                 align_elements: Union[InheritType,Literal["top", "center", "bottom"]] = INHERIT
                 ):

        self.background: Optional[Material] = background

        self.root: Optional[View] = None
        self.parent: Optional[Element] = None

        self._fit_width: int = 0
        self._fit_height: int = 0

        self.set_style(style)

        self.spacing: int = self._style.spacing if spacing is INHERIT else spacing
        if self.spacing:
            self.min_spacing: int = self.spacing
        else:
            self.min_spacing: int = self._style.min_spacing if min_spacing is INHERIT else min_spacing

        self.focus_self: bool = self._style.focus_self if focus_self is INHERIT else focus_self

        self.align_elements: Literal["top", "center", "bottom"] = self._style.align_elements_v \
            if align_elements is INHERIT else align_elements

        self._elements = []
        self.set_elements(*elements, _supress_update=True)
        super().__init__(size, width, height,
                         default_size=(FILL if any(i._width.mode == 2 for i in self._elements) else FIT,
                                       FILL if any(i._height.mode == 2 for i in self._elements) else FIT))
        self._update_elements()

    def __repr__(self):
        return f"<HStack({len(self._elements)} elements)>"

    def _update_rect_chain_up(self) -> NoReturn:
        log.size.info(self, "Chain up.")
        if self._width.mode == 1:
            if self._elements:
                total_width = 0
                for i in self.elements:
                    if i._width.mode == 2:
                        raise ValueError("Cannot have elements of FILL width inside of a FIT width HStack.")
                    total_width += i.get_abs_width(0)
                self._fit_width = total_width + self.min_spacing * (len(self._elements) - 1)
            else:
                self._fit_width = 20

        if self._height.mode == 1:
            if self._elements:
                if any(i._height.mode == 2 for i in self._elements):
                    raise ValueError("Cannot have elements of FILL height inside of a FIT height HStack.")
                self._fit_height = max(i.get_abs_height(0) for i in self._elements)
            else:
                self._fit_height = 20

        log.size.info(self, f"Fit size set to ({self._fit_width}, {self._fit_height}).")
        self.can_focus = any(i._can_focus for i in self._elements)
        if self.parent:
            self.parent._update_rect_chain_up()
            self.root.check_size = True

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                root: "View", _ignore_fill_width: bool = False,
                                _ignore_fill_height: bool = False) -> NoReturn:

        # Calculate own width
        stack_width = self.get_abs_width(max_size[0])
        padding = self._width.value if self._width.mode == 1 else 0

        # Calculate the total width of the elements, and the spacing between them
        width_of_elements = 0
        element_fill_width = 0
        element_fill_count = 0
        for i in self._elements:
            if i._width.mode == 2:
                element_fill_width += i._width.percentage
                element_fill_count += 1
            else:
                width_of_elements += i.get_abs_width(0)

        if self.spacing is not None:
            spacing = self.spacing

        elif element_fill_width == 0:
            if len(self._elements) == 1:
                spacing = 0
            else:
                spacing = max(self.min_spacing,
                              int((round(stack_width) - padding - width_of_elements) / (len(self._elements) - 1)))
        else:
            spacing = self.min_spacing

        remaining_width = stack_width - padding - width_of_elements - spacing * (len(self._elements) - 1)

        # Update own width and height
        stack_height = self.get_abs_height(max_size[1])

        super()._update_rect_chain_down(surface, pos, max_size, root)

        # Update width and height of elements
        if not self._elements:
            return

        if element_fill_width == 0 and (self.spacing is not None or len(self._elements) == 1):
            x = remaining_width / 2 + padding / 2
            x += pos[0] - self.rect.x
        else:
            x = padding / 2

        if element_fill_count:
            remainder = remaining_width % element_fill_count
            left_rem = math.ceil(remainder / 2) if pos[0] - self.rect.x > 0 else remainder // 2
            fill_n = -1

        self._first_visible_element = None

        with log.size.indent:
            for n, element in enumerate(self._elements):
                if self.align_elements == "center":
                    y = pos[1] + stack_height / 2 - element.get_abs_height(stack_height) / 2
                elif self.align_elements == "top":
                    y = pos[1]
                else:
                    y = pos[1] + stack_height - element.get_abs_height(self.rect.h)

                if element._width.mode == 2:
                    fill_n += 1
                    w = remaining_width // element_fill_width * element._height.percentage
                    if fill_n < left_rem or fill_n >= element_fill_count - (remainder - left_rem):
                        w += 1
                else:
                    w = element.get_abs_width(0)

                element._update_rect_chain_down(surface, (self.rect.x + x, y),
                                                max_size=(w, self.rect.h),
                                                root=root, _ignore_fill_width=True)

                if self.rect.x + x + w < surface.get_abs_offset()[0] or \
                        self.rect.x + x > surface.get_abs_offset()[0] + surface.get_width():
                    element.is_visible = False
                else:
                    element.is_visible = True
                    if self._first_visible_element is None:
                        self._first_visible_element = n

                x += spacing + w

    def _focus_chain(self, root: View, previous=None, direction: str = 'in') -> Element:
        looking_for = root.element_focused if previous is None else previous

        if root.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(root, self, direction=direction)

        if direction in {'left', 'right', 'forward', 'backward'}:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = len(self._elements) - 1 if direction == 'left' else 0

            if direction in {'left', 'backward'}:
                end = 0
                amount = -1
            else:
                end = len(self._elements) - 1
                amount = 1

            # Find an element that we can select
            while index != end:
                index += amount
                element = self._elements[index]
                if element._can_focus:
                    log.nav.info(self, f"-> child {element}.")
                    return element._focus_chain(root, None)

            # If no element is found, return to the parent
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(root, self, direction=direction)

        elif direction in {'up', 'down'}:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(root, self, direction=direction)

        elif direction == "out":
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self
            else:
                log.nav.info(self, f"-> parent {self.parent}.")
                return self.parent._focus_chain(root, self, direction=direction)

        else:
            return self._enter_in_first_element(root, direction)

    def _enter_in_first_element(self, root: View, direction: str,
                                ignore_self_focus: bool = False) -> Optional[Element]:

        # The stack is being entered, so select the element closest to the previous element
        if self.focus_self and not ignore_self_focus:
            log.nav.info(self, "Returning self.")
            return self

        if (not ignore_self_focus) and \
                (root.element_focused is not None) and \
                self._style.focus_on_entry == 'closest' and \
                direction != "in_first":

            closest_elements = sorted(self._elements,
                                      key=lambda x: abs(x.rect.centerx - root.element_focused.rect.centerx))
            for element in closest_elements:
                if element._can_focus:
                    closest_element = element
                    break
            else:
                return None
        else:
            for element in self._elements:
                if element._can_focus:
                    closest_element = element
                    break
            else:
                return None
        log.nav.info(self, f"-> child {closest_element}.")

        if direction == "in_first":
            direction = "in"
        return closest_element._focus_chain(root, None, direction=direction)
