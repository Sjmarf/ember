import math
import pygame
from .. import common as _c
from ..common import INHERIT, InheritType, FocusType, FOCUS_CLOSEST
from typing import Union, Optional, Sequence, TYPE_CHECKING

from .base.stack import Stack
from .. import log
from ..size import SizeType, SequenceSizeType, SizeMode, Size
from ..position import (
    PositionType,
    SequencePositionType,
    Position,
    OptionalSequencePositionType,
)

from .base.element import Element


if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle
    from ..state.state import State
    from .view import ViewLayer
    from ..material.material import Material


class HStack(Stack):
    def __init__(
        self,
        *elements: Union[Element, Sequence[Element]],
        material: Union["State", "Material", None] = None,
        spacing: Union[InheritType, int] = INHERIT,
        min_spacing: Union[InheritType, int] = INHERIT,
        focus_on_entry: Union[InheritType, FocusType] = INHERIT,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
    ):
        self.layer: Optional[ViewLayer] = None
        self.parent: Optional[Element] = None

        self._elements = []
        self.set_elements(*elements, _update=False)
        super().__init__(
            style,
            material,
            spacing,
            min_spacing,
            focus_on_entry,
            rect,
            pos,
            x,
            y,
            size,
            width,
            height,
            content_pos,
            content_x,
            content_y,
        )

        self._update_elements()

        self.content_h: Optional[Size] = (
            self._style.content_size[1] if content_h is None else Size._load(content_h)
        )

    def __repr__(self) -> str:
        return f"<HStack({len(self._elements)} elements)>"

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        # This is the additional padding caused by a width value such as ember.FIT + 20
        horizontal_padding = (
            self._active_w.value if self._active_w.mode == SizeMode.FIT else 0
        )

        # Calculate the total width of the elements
        total_width_of_elements = 0
        total_element_fill_width = 0
        element_fill_count = 0
        for i in self._elements:
            i.set_active_width()
            if i._active_w.mode == SizeMode.FILL:
                total_element_fill_width += i._active_w.percentage
                element_fill_count += 1
            else:
                total_width_of_elements += i.get_abs_width()

        # Find the spacing between the elements
        if self.spacing is not None:
            spacing = self.spacing

        elif total_element_fill_width == 0:
            if len(self._elements) == 1:
                spacing = 0
            else:
                spacing = max(
                    self.min_spacing,
                    int(
                        (round(w) - horizontal_padding - total_width_of_elements)
                        / (len(self._elements) - 1)
                    ),
                )
        else:
            spacing = self.min_spacing

        remaining_width = (
            round(w)
            - horizontal_padding
            - total_width_of_elements
            - spacing * (len(self._elements) - 1)
        )

        # Update own rect
        super()._update_rect_chain_down(surface, x, y, w, h)

        if not self._elements:
            return

        # Find the x position of the first child element
        if total_element_fill_width == 0 and (
            self.spacing is not None or len(self._elements) == 1
        ):
            if self._active_w.mode == SizeMode.FIT:
                element_x = remaining_width / 2 + horizontal_padding / 2
            else:
                element_x = self.content_x.get(
                    w,
                    total_width_of_elements + spacing * (len(self._elements) - 1),
                )
            #element_x += x - self.rect.x
        else:
            element_x = horizontal_padding / 2

        # This is used to equally split the remaining size up between elements with a FILL width
        if element_fill_count != 0:
            remainder = remaining_width % element_fill_count
            left_rem = (
                math.ceil(remainder / 2) if x - self.rect.x > 0 else remainder // 2
            )
            fill_n = -1

        self._first_visible_element = None

        # Iterate over child elements
        with log.size.indent:
            for n, element in enumerate(self._elements):
                element.set_active_height(self.content_h)
                # We've already set the active width further up; we don't need to do it again

                # Find the y position of the child element
                element_y_obj = element._y if element._y is not None else self.content_y
                element_y = y + element_y_obj.get(
                    h,
                    element.get_abs_height(h - abs(element_y_obj.value)),
                )

                if element._active_w.mode == SizeMode.FILL:
                    fill_n += 1
                    element_w = (
                        remaining_width
                        // total_element_fill_width
                        * element._active_w.percentage
                        + element._active_w.value
                    )
                    element_x -= element._active_w.value / 2
                    if fill_n < left_rem or fill_n >= element_fill_count - (
                        remainder - left_rem
                    ):
                        element_w += 1
                else:
                    element_w = element.get_abs_width()

                # Determine whether the element is visible on screen or not
                if not self.is_visible:
                    element.is_visible = False
                elif (
                    self._int_rect.x + element_x + element_w
                    < surface.get_abs_offset()[0]
                    or self._int_rect.x + element_x
                    > surface.get_abs_offset()[0] + surface.get_width()
                ):
                    element.is_visible = False
                else:
                    element.is_visible = True
                    if self._first_visible_element is None:
                        self._first_visible_element = n

                # Start the chain for the child element
                element._update_rect_chain_down(
                    surface,
                    self._int_rect.x + element_x,
                    element_y,
                    element_w,
                    element.get_abs_height(h - abs(element_y_obj.value)),
                )

                # Increment the x position for the next child element
                element_x += spacing + element_w
                if element._active_w.mode == SizeMode.FILL:
                    element_x -= element._active_w.value / 2

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._elements:
            total_width = 0
            for i in self.elements:
                total_width += i.get_abs_width()
            self._min_w = total_width + self.min_spacing * (len(self._elements) - 1)
            self._min_h = max(i.get_abs_height() for i in self._elements)
        else:
            self._min_w = 20
            self._min_h = 20

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        looking_for = self.layer.element_focused if previous is None else previous

        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
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
                    log.nav.info(self, f"-> child {element}.")
                    return element._focus_chain(_c.FocusDirection.IN)

        log.nav.info(self, f"-> parent {self.parent}.")
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
        log.nav.info(self, f"-> child {closest_element}.")

        direction = _c.FocusDirection.IN
        return closest_element._focus_chain(direction)
