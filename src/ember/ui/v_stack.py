import math
import pygame
from .. import common as _c
from ..common import INHERIT, InheritType, FocusType, FOCUS_CLOSEST
from typing import Union, Optional, Sequence, TYPE_CHECKING, Generator

from .base.stack import Stack
from .. import log
from ..size import SizeType, OptionalSequenceSizeType, FitSize, FillSize
from ..position import (
    PositionType,
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
        *elements: Union[Element, Sequence[Element], Generator[Element, None, None]],
        material: Union["State", "Material", None] = None,
        spacing: Union[InheritType, int] = INHERIT,
        min_spacing: Union[InheritType, int] = INHERIT,
        focus_on_entry: Union[InheritType, FocusType] = INHERIT,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
    ):
        self.layer: Optional[ViewLayer] = None
        self.parent: Optional[Element] = None

        self._elements = []

        super().__init__(
            elements=elements,
            material=material,
            spacing=spacing,
            min_spacing=min_spacing,
            focus_on_entry=focus_on_entry,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
            style=style,
        )

    def __repr__(self) -> str:
        return f"<VStack({len(self._elements)} elements)>"

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        # Update own rect
        super()._update_rect_chain_down(surface, x, y, w, h)

        if not self._elements:
            return

        # This is the additional padding caused by a height value such as ember.FIT + 20
        vertical_padding = (
            self._active_h.value if isinstance(self._active_h, FitSize) else 0
        )

        spacing = self._get_element_spacing(
            vertical_padding, isinstance(self._active_h, FitSize)
        )

        remaining_height = (
            h
            - vertical_padding
            - self._total_size_of_nonfill_elements
            - spacing * (len(self._elements) - 1)
        )

        # Find the y position of the first child element
        if self._fill_element_count == 0 and (
            self.spacing is not None or len(self._elements) == 1
        ):
            if isinstance(self._active_w, FitSize):
                element_y = remaining_height / 2 + vertical_padding / 2
            else:
                element_y = self.content_y.get(
                    h,
                    self._total_size_of_nonfill_elements
                    + spacing * (len(self._elements) - 1),
                )
        else:
            element_y = vertical_padding / 2

        # This is used to equally split the remaining size up between elements with a FILL height
        if self._fill_element_count != 0:
            remainder = remaining_height % self._fill_element_count
            top_rem = math.ceil(remainder / 2) if h % 2 == 1 else remainder // 2
            bottom_rem = remainder - top_rem
            fill_n = -1

            if abs(self._int_rect.y - y) not in {0, 1}:
                if top_rem > bottom_rem:
                    element_y -= 0.5

                if bottom_rem > top_rem:
                    element_y += 0.5


        self._first_visible_element = None

        # Iterate over child elements
        with log.size.indent:
            for n, element in enumerate(self._elements):
                element.set_active_w(self._content_w)
                # We've already set the active height in update_rect_chain_up; we don't need to do it again

                # Find the x position of the child element
                element_x_obj = element._x if element._x is not None else self.content_x
                element_x = x + element_x_obj.get(
                    w,
                    element.get_abs_w(w - abs(element_x_obj.value)),
                )

                # Find the height of the child element
                if isinstance(element._active_h, FillSize):
                    fill_n += 1
                    element_h = (
                        remaining_height
                        // self._total_size_of_fill_elements
                        * element._active_h.percentage
                        + element._active_h.value
                    )
                    if (
                        fill_n < top_rem
                        or fill_n >= self._fill_element_count - bottom_rem
                    ):
                        element_h += 1
                else:
                    element_h = element.get_abs_h()

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
                    element.get_abs_w(w - abs(element_x_obj.value)),
                    int(element_h),
                )

                # Increment the y position for the next child element
                element_y += spacing + element_h

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._elements:
            self._fill_element_count = 0
            self._total_size_of_fill_elements = 0
            self._total_size_of_nonfill_elements = 0

            for i in self.elements:
                i.set_active_h(self._content_h)
                if isinstance(i._active_h, FillSize):
                    self._total_size_of_fill_elements += i._active_h.percentage
                    self._fill_element_count += 1
                else:
                    self._total_size_of_nonfill_elements += i.get_abs_h()

            self._min_h = self._total_size_of_nonfill_elements + self.min_spacing * (
                len(self._elements) - 1
            )
            self._min_w = max(i.get_abs_w() for i in self._elements)
        else:
            self._min_w, self._min_h = 20, 20

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
