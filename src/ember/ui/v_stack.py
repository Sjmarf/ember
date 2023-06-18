import math
import pygame
from .. import common as _c
from ..common import INHERIT, InheritType, FocusType, FOCUS_CLOSEST
from typing import Union, Optional, Sequence, TYPE_CHECKING

from .base.stack import Stack
from .. import log
from ..size import SizeType, SequenceSizeType, SizeMode, Size, OptionalSequenceSizeType
from ..position import (
    PositionType,
    Position,
    SequencePositionType,
    OptionalSequencePositionType,
)

from .base.element import Element

if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle
    from ..state.state import State
    from .view import ViewLayer
    from ..material.material import Material


class VStack(Stack):
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
        content_w: Optional[SizeType] = None,
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

        self.content_w: Optional[Size] = (
            self._style.content_size[0]
            if content_w is INHERIT
            else Size._load(content_w)
        )

    def __repr__(self) -> str:
        return f"<VStack({len(self._elements)} elements)>"

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        # This is the additional padding caused by a height value such as ember.FIT + 20
        vertical_padding = (
            self._active_h.value if self._active_h.mode == SizeMode.FIT else 0
        )

        # Calculate the total height of the elements
        total_height_of_elements = 0
        total_element_fill_height = 0
        element_fill_count = 0
        for i in self._elements:
            i.set_active_height()
            if i._active_h.mode == SizeMode.FILL:
                total_element_fill_height += i._active_h.percentage
                element_fill_count += 1
            else:
                total_height_of_elements += i.get_abs_height()

        # Find the spacing between the elements
        if self.spacing is not None:
            spacing = self.spacing

        elif total_element_fill_height == 0:
            if len(self._elements) == 1:
                spacing = 0
            else:
                spacing = max(
                    self.min_spacing,
                    int(
                        (round(h) - total_height_of_elements - vertical_padding)
                        / (len(self._elements) - 1)
                    ),
                )
        else:
            spacing = self.min_spacing

        remaining_height = (
            h
            - vertical_padding
            - total_height_of_elements
            - spacing * (len(self._elements) - 1)
        )

        # Update own rect
        super()._update_rect_chain_down(surface, x, y, w, h)

        if not self._elements:
            return

        # Find the y position of the first child element
        if total_element_fill_height == 0 and (
            self.spacing is not None or len(self._elements) == 1
        ):
            if self._active_h.mode == SizeMode.FIT:
                element_y = remaining_height / 2 + vertical_padding / 2
            else:
                element_y = self.content_y.get(
                    h,
                    total_height_of_elements + spacing * (len(self._elements) - 1),
                )
            element_y += y - self.rect.y
        else:
            element_y = vertical_padding / 2

        # This is used to equally split the remaining size up between elements with a FILL height
        if element_fill_count != 0:
            remainder = remaining_height % element_fill_count
            # The amount of remainder height that is distributed to elements each side of the stack
            top_rem = (
                math.ceil(remainder / 2) if y - self.rect.y > 0 else remainder // 2
            )
            fill_n = -1

        self._first_visible_element = None

        # Iterate over child elements
        with log.size.indent:
            for n, element in enumerate(self._elements):
                element.set_active_width(self.content_w)
                # We've already set the active height further up; we don't need to do it again

                # Find the x position of the child element
                element_x_obj = element._x if element._x is not None else self.content_x
                element_x = x + element_x_obj.get(
                    w,
                    element.get_abs_width(w - abs(element_x_obj.value)),
                )

                # Find the height of the child element
                if element._active_h.mode == SizeMode.FILL:
                    fill_n += 1
                    element_h = (
                        remaining_height
                        // total_element_fill_height
                        * element._active_h.percentage
                        + element._active_h.value
                    )
                    element_y -= element._active_h.value / 2
                    if fill_n < top_rem or fill_n >= element_fill_count - (
                        remainder - top_rem
                    ):
                        element_h += 1
                else:
                    element_h = element.get_abs_height()

                # Determine whether the element is visible on screen or not
                if not self.is_visible:
                    element.is_visible = False
                elif (
                    self._int_rect.y + element_y + element_h
                    <= surface.get_abs_offset()[1]
                    or self._int_rect.y + element_y
                    >= surface.get_abs_offset()[1] + surface.get_height()
                ):
                    element.is_visible = False
                else:
                    element.is_visible = True
                    if self._first_visible_element is None:
                        self._first_visible_element = n

                # Start the chain for the child element
                element._update_rect_chain_down(
                    surface,
                    element_x,
                    y + element_y,
                    element.get_abs_width(self.rect.w - abs(element_x_obj.value)),
                    element_h,
                )

                # Increment the y position for the next child element
                element_y += spacing + element_h
                if element._active_h.mode == SizeMode.FILL:
                    element_y -= element._active_h.value / 2

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._elements:
            self._min_w = max(i.get_abs_width() for i in self._elements)
            total_height = 0
            for i in self.elements:
                total_height += i.get_abs_height()
            self._min_h = total_height + self.min_spacing * (len(self._elements) - 1)
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
            _c.FocusDirection.UP,
            _c.FocusDirection.DOWN,
            _c.FocusDirection.FORWARD,
            _c.FocusDirection.BACKWARD,
        }:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = (
                    len(self._elements) - 1 if direction == _c.FocusDirection.UP else 0
                )

            if direction in {_c.FocusDirection.UP, _c.FocusDirection.BACKWARD}:
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
                    x.rect.centery - self.layer.element_focused.rect.centery
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

        return closest_element._focus_chain(_c.FocusDirection.IN)
