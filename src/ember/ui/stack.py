import pygame
import math

from typing import Optional, TYPE_CHECKING

from ember import log
from ember import axis

from ember import common as _c
from ember.common import (
    SequenceElementType,
    FOCUS_CLOSEST,
    FOCUS_AXIS_FORWARD,
    FOCUS_AXIS_BACKWARD,
    FocusDirection,
)
from ember.ui.element import Element
from .focus_passthrough import FocusPassthrough

from ember.trait.trait import Trait
from ember.spacing import SpacingType, FILL_SPACING, load_spacing
from ember.size import FillSize, FitSize, AbsoluteSize

if TYPE_CHECKING:
    pass


class Stack(FocusPassthrough):
    """
    A Stack is a collection of Elements. There are two subclasses of Stack - :py:class:`ember.ui.VStack`
    and :py:class:`ember.ui.HStack`.
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

        super().__init__(*elements, **kwargs)

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        elements = list(self._elements_to_render)
        spacing = self.spacing.get_min()

        unallocated_space = self.rect.rel_size1 - spacing * (len(elements) - 1)

        element_sizes: dict[Element, float] = {}

        for n, element in enumerate(
            sorted(
                elements,
                key=lambda i: (int(i.rel_size1.relies_on_max_value)),
            )
        ):
            element: Element
            max_size = unallocated_space / (len(elements) - n)
            size = element.get_abs_rel_size1(max_size)
            unallocated_space -= size
            element_sizes[element] = size

        if unallocated_space:
            spacing = self.spacing.get(
                spacing + int(unallocated_space / (len(elements) - 1))
            )

        element_rel_pos1 = (
            self.rect.rel_size1 / 2
            - (sum(element_sizes.values()) + spacing * (len(elements) - 1)) / 2
        )

        for element in elements:
            element_rel_size1 = element_sizes[element]
            element_rel_pos2 = element.rel_pos2.get(
                self.rect.rel_size2,
                element.get_abs_rel_size2(
                    self.rect.rel_size2 - abs(element.rel_pos2.value)
                ),
                self.axis,
            )

            element.update_rect(
                surface,
                rel_pos1=self.rect.rel_pos1 + element_rel_pos1,
                rel_pos2=self.rect.rel_pos2 + element_rel_pos2,
                rel_size2=element.get_abs_rel_size2(
                    self.rect.rel_size2 - abs(element.rel_pos2.value)
                ),
                rel_size1=element_rel_size1,
            )
            element_rel_pos1 += element_rel_size1 + spacing

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
            FOCUS_AXIS_BACKWARD[axis.axis],
            FOCUS_AXIS_FORWARD[axis.axis],
            FocusDirection.FORWARD,
            FocusDirection.BACKWARD,
        }:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = (
                    len(self._elements) - 1
                    if direction == FOCUS_AXIS_FORWARD[axis.axis]
                    else 0
                )

            if direction in {
                FOCUS_AXIS_FORWARD[axis.axis],
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
