import pygame
import math

from typing import Optional, TYPE_CHECKING

from ember import log
from ember import axis

from ember import common as _c
from ember.common import SequenceElementType, FocusDirection, FOCUS_CLOSEST
from ember.base.element import Element
from .focus_passthrough import FocusPassthrough

from ember.trait.trait import Trait
from ember.spacing import SpacingType, FILL_SPACING, load_spacing
from ember.size import FillSize, FitSize
from ..base.can_pivot import CanPivot

if TYPE_CHECKING:
    pass


class Stack(FocusPassthrough):
    """
    A Stack is a collection of Elements. There are two subclasses of Stack - :py:class:`ember.ui.VStack`
    and :py:class:`ember.ui.HStack`. This base class should not be instantiated directly.
    """

    spacing = Trait(
        FILL_SPACING,
        on_update=lambda self: self.update_min_size_next_tick(self),
        load_value_with=load_spacing,
    )

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        spacing: Optional[SpacingType] = None,
        **kwargs,
    ):
        self._first_visible_element: Optional[Element] = None

        self.spacing = spacing

        super().__init__(
            # MultiElementContainer
            *elements,
            **kwargs,
        )

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        if not self._elements:
            return

        fill_element_count = 0
        total_size_of_fill_elements = 0
        total_size_of_nonfill_elements = 0

        for i in self.elements:
            if i is None:
                continue
            if isinstance(i.rel_size1, FillSize):
                total_size_of_fill_elements += i.rel_size1.fraction
                fill_element_count += 1
            else:
                total_size_of_nonfill_elements += i.get_abs_rel_size1()

        # This is the additional padding caused by a rel_size1 value such as ember.FIT + 20
        parallel_padding = (
            self.rel_size1.offset if isinstance(self.rel_size1, FitSize) else 0
        )
        
        if len(self._elements) == 1:
            spacing = 0

        elif fill_element_count > 0 or isinstance(self.rel_size1, FitSize):
            spacing = self.spacing.get_min()

        else:
            spacing = self.spacing.get(
                int(
                    (self.rect.rel_size1 - parallel_padding - total_size_of_nonfill_elements)
                    / (len(self._elements) - 1)
                ),
            )        

        # The parallel space that is available to divide among FILL elements
        remaining_space = (
            self.rect.rel_size1
            - parallel_padding
            - total_size_of_nonfill_elements
            - spacing * (len(self._elements) - 1)
        )

        # Find the starting position of the first child element
        if fill_element_count == 0:
            if isinstance(self.rel_size1, FitSize):
                element_rel_pos1 = remaining_space / 2 + parallel_padding / 2
            else:
                element_rel_pos1 = (
                    self.rect.rel_size1 / 2
                    - (
                        total_size_of_nonfill_elements
                        + spacing * (len(self._elements) - 1)
                    )
                    / 2
                )
        else:
            element_rel_pos1 = parallel_padding / 2

        # This is used to equally split the remaining size up between elements with a FILL size
        if fill_element_count != 0:
            remainder = remaining_space % fill_element_count
            leading_remainder = (
                math.ceil(remainder / 2)
                if self.rect.rel_size1 % 2 == 0
                else remainder // 2
            )
            trailing_remainder = remainder - leading_remainder
            fill_n = -1

            if abs(int(self.rect.rel_pos1) - self.rect.rel_pos1) not in {0, 1}:
                if leading_remainder > trailing_remainder:
                    element_rel_pos1 -= 0.5

                if trailing_remainder > leading_remainder:
                    element_rel_pos1 += 0.5

        self._first_visible_element = None

        # Iterate over child elements
        with log.size.indent():
            for n, element in enumerate(self._elements):
                element_rel_pos2 = element.rel_pos2.get(
                    self.rect.rel_size2,
                    element.get_abs_rel_size2(
                        self.rect.rel_size2 - abs(element.rel_pos2.value)
                    ),
                    self.axis
                )

                # Find the height of the child element
                if isinstance(element.rel_size1, FillSize):
                    fill_n += 1
                    element_rel_size1 = (
                        remaining_space
                        // total_size_of_fill_elements
                        * element.rel_size1.fraction
                        + element.rel_size1.offset
                    )
                    if (
                        fill_n < leading_remainder
                        or fill_n >= fill_element_count - trailing_remainder
                    ):
                        element_rel_size1 += 1
                else:
                    element_rel_size1 = element.get_abs_rel_size1()

                # Determine whether the element is visible on screen or not
                if not self.visible:
                    element.visible = False
                elif (
                    self.rect.rel_pos1 + element_rel_pos1 + element_rel_size1
                    <= surface.get_abs_offset()[axis.axis]
                    or self.rect.rel_pos1 + element_rel_pos1
                    >= surface.get_abs_offset()[axis.axis]
                    + surface.get_size()[axis.axis]
                ):
                    element.visible = False
                else:
                    element.visible = True
                    if self._first_visible_element is None:
                        self._first_visible_element = n

                # Start the chain for the child element
                element.update_rect(
                    surface,
                    rel_pos1=self.rect.rel_pos1 + element_rel_pos1,
                    rel_pos2=self.rect.rel_pos2 + element_rel_pos2,
                    rel_size2=element.get_abs_rel_size2(
                        self.rect.rel_size2 - abs(element.rel_pos2.value)
                    ),
                    rel_size1=element_rel_size1,
                )

                # Increment the y position for the next child element
                element_rel_pos1 += spacing + element_rel_size1

    def _update_min_size(self) -> None:
        if self._elements:
            size = 0
            for i in self.elements:
                if i is not None:
                    if not isinstance(i.rel_size1, FillSize):
                        size += i.get_abs_rel_size1()

            self._min_size.rel_size1 = size + self.spacing.get_min() * (
                len(self._elements) - 1
            )
            self._min_size.rel_size2 = max(
                [i.get_abs_rel_size2() for i in self._elements if i is not None]
                or (20,)
            )
        else:
            self._min_size.rel_size1, self._min_size.rel_size2 = 20, 20

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        for n, i in enumerate(self._elements[self._first_visible_element :]):
            if not i.visible:
                break
            i.render(surface, offset, alpha=alpha)

    def _update(self) -> None:
        for i in self._elements[self._first_visible_element :]:
            i.update()
            if not i.visible:
                break

    def _event(self, event: pygame.event.Event) -> bool:
        for i in self._elements[self._first_visible_element :]:
            if i is None:
                continue
            if i._event(event):
                return True
            if not i.visible:
                break
        return False

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        looking_for = self.layer.element_focused if previous is None else previous
        if self.layer.element_focused is self:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent.focus_chain(direction, previous=self)

        if direction in {
            FocusDirection.IN,
            FocusDirection.IN_FIRST,
            FocusDirection.SELECT,
        }:
            return self._enter_in_first_element(direction)

        if direction in {
            FocusDirection.AXIS_FORWARD[axis.axis],
            FocusDirection.AXIS_BACKWARD[axis.axis],
            FocusDirection.FORWARD,
            FocusDirection.BACKWARD,
        }:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = (
                    len(self._elements) - 1
                    if direction == FocusDirection.AXIS_BACKWARD[axis.axis]
                    else 0
                )

            if direction in {
                FocusDirection.AXIS_BACKWARD[axis.axis],
                FocusDirection.BACKWARD,
            }:
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
                    log.nav.info(f"-> child {element}.")
                    return element.focus_chain(_c.FocusDirection.IN)

        log.nav.info(f"-> parent {self.parent}.")
        return self.parent.focus_chain(direction, previous=self)

    def _enter_in_first_element(
        self, direction: _c.FocusDirection, ignore_self_focus: bool = False
    ) -> Optional[Element]:
        # The stack is being entered, so select the element closest to the previous element
        if (
            (not ignore_self_focus)
            and (self.layer.element_focused is not None)
            and self.focus_on_entry is FOCUS_CLOSEST
            and direction != _c.FocusDirection.IN_FIRST
        ):
            comparison = (
                self.layer.element_focused.rect.rel_pos1
                + self.layer.element_focused.rect.rel_size1 / 2
            )
            closest_elements = sorted(
                self._elements,
                key=lambda x: abs(x.rect.rel_pos1 + x.rect.rel_size1 / 2 - comparison),
            )
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

        log.nav.info(f"-> child {closest_element}.")
        return closest_element.focus_chain(_c.FocusDirection.IN)
