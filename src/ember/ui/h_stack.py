import math
import pygame
from .. import common as _c
from ..common import FOCUS_CLOSEST, SequenceElementType, FocusType
from typing import Optional, Union, Sequence, TYPE_CHECKING

from ember.base.directional_stack import DirectionalStack
from .. import log
from ..size import FitSize, FillSize
from ..base.element import Element
from ..base.content_size_direction import HorizontalContentSize
from ..base.content_pos_direction import PerpendicularContentY
from ember.size import SizeType, OptionalSequenceSizeType
from ember.position import (
    PositionType,
    SequencePositionType,
)
from ..spacing import SpacingType



class HStack(PerpendicularContentY, HorizontalContentSize, DirectionalStack):
    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        spacing: Optional[SpacingType] = None,
        focus_on_entry: Optional[FocusType] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
    ):
        super().__init__(
            # Stack
            *elements,
            spacing=spacing,
            focus_on_entry=focus_on_entry,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
            # ContentX
            content_y=content_y,
        )

    def __repr__(self) -> str:
        return f"<HStack({len(self._elements)} elements)>"

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        if not self._elements:
            return

        self._fill_element_count = 0
        self._total_size_of_fill_elements = 0
        self._total_size_of_nonfill_elements = 0

        for i in self._elements:
            if isinstance(i.w, FillSize):
                self._total_size_of_fill_elements += i.w.fraction
                self._fill_element_count += 1
            else:
                self._total_size_of_nonfill_elements += i.get_abs_w()

        # This is the additional padding caused by a width value such as ember.FIT + 20
        horizontal_padding = (
            self.w.value if isinstance(self.w, FitSize) else 0
        )
        spacing = self._get_element_spacing(
            self.rect.w, horizontal_padding, isinstance(self.w, FitSize)
        )

        # The width that is available to divide among FILL elements
        remaining_width = (
            w
            - horizontal_padding
            - self._total_size_of_nonfill_elements
            - spacing * (len(self._elements) - 1)
        )

        # Find the x position of the first child element
        if self._fill_element_count == 0:
            if isinstance(self.w, FitSize):
                element_x = remaining_width / 2 + horizontal_padding / 2
            else:
                element_x = (
                    w / 2
                    - (
                        self._total_size_of_nonfill_elements
                        + spacing * (len(self._elements) - 1)
                    )
                    / 2
                )
        else:
            element_x = horizontal_padding / 2

        # This is used to equally split the remaining size up between elements with a FILL width
        if self._fill_element_count != 0:
            remainder = remaining_width % self._fill_element_count
            left_rem = math.ceil(remainder / 2) if w % 2 == 1 else remainder // 2
            right_rem = remainder - left_rem
            fill_n = -1

            if abs(self._int_rect.x - x) not in {0, 1}:
                if left_rem > right_rem:
                    element_x -= 0.5

                if right_rem > left_rem:
                    element_x += 0.5

        self._first_visible_element = None

        # Iterate over child elements
        with log.size.indent():
            for n, element in enumerate(self._elements):
                # Find the y position of the child element
                element_y = y + element.y.get(
                    h,
                    element.get_abs_h(h - abs(element.y.value)),
                )

                # Find the width of the child element
                if isinstance(element.w, FillSize):
                    fill_n += 1
                    element_w = (
                        remaining_width
                        // self._total_size_of_fill_elements
                        * element.w.fraction
                        + element.w.offset
                    )
                    if (
                        fill_n < left_rem
                        or fill_n >= self._fill_element_count - right_rem
                    ):
                        element_w += 1
                else:
                    element_w = element.get_abs_w()

                # Determine whether the element is visible on screen or not
                if not self.visible:
                    element.visible = False
                elif (
                    self._int_rect.x + element_x + element_w
                    < surface.get_abs_offset()[0]
                    or self._int_rect.x + element_x
                    > surface.get_abs_offset()[0] + surface.get_width()
                ):
                    element.visible = False
                else:
                    element.visible = True
                    if self._first_visible_element is None:
                        self._first_visible_element = n

                # Start the chain for the child element
                element.update_rect(
                    surface,
                    x + element_x,
                    element_y,
                    element_w,
                    element.get_abs_h(h - abs(element.y.value)),
                )

                # Increment the x position for the next child element
                element_x += spacing + element_w

    def _update_min_size(self) -> None:
        if self._elements:
            size = 0
            for i in self.elements:
                if not isinstance(i.w, FillSize):
                    size += i.get_abs_w()

            self._min_w = size + self.spacing.get_min() * (
                len(self._elements) - 1
            )
            self._min_h = max(i.get_abs_h() for i in self._elements)
        else:
            self._min_w, self._min_h = 20, 20

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        looking_for = self.layer.element_focused if previous is None else previous

        if self.layer.element_focused is self:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        if direction in {
            _c.FocusDirection.IN,
            _c.FocusDirection.IN_FIRST,
            _c.FocusDirection.SELECT,
        }:
            return self._enter_in_first_element(direction)

        if direction in {
            _c.FocusDirection.LEFT,
            _c.FocusDirection.RIGHT,
            _c.FocusDirection.FORWARD,
            _c.FocusDirection.BACKWARD,
        }:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = (
                    len(self._elements) - 1
                    if direction == _c.FocusDirection.LEFT
                    else 0
                )

            if direction in {_c.FocusDirection.LEFT, _c.FocusDirection.BACKWARD}:
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
                    return element._focus_chain(_c.FocusDirection.IN)

        log.nav.info(f"-> parent {self.parent}.")
        return self.parent._focus_chain(direction, previous=self)

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
            closest_elements = sorted(
                self._elements,
                key=lambda x: abs(
                    x.rect.centerx - self.layer.element_focused.rect.centerx
                ),
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
        return closest_element._focus_chain(_c.FocusDirection.IN)
