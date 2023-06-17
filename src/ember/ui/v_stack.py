import math
import pygame
from .. import common as _c
from ..common import INHERIT, InheritType, FocusType, FOCUS_CLOSEST, FOCUS_FIRST
from typing import Union, Optional, Sequence, Literal, TYPE_CHECKING

from .base.stack import Stack
from .. import log
from ..size import FIT, FILL, SizeType, SequenceSizeType, SizeMode
from ..position import PositionType, Position, CENTER, SequencePositionType
from .view import ViewLayer
from .base.element import Element
from ..material.material import Material
from ..state.state import State

if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle


class VStack(Stack):
    def __init__(
        self,
        *elements: Union[Element, Sequence[Element]],
        material: Union["State", Material, None] = None,
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
        content_x: Union[InheritType, Position] = INHERIT,
        content_y: Union[InheritType, Position] = INHERIT,
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
        )
        self._update_elements()

        self.content_x: Position = self._style.content_pos[0] if content_x is INHERIT else content_x
        self.content_y: Position = self._style.content_pos[1] if content_y is INHERIT else content_y

    def __repr__(self) -> str:
        return f"<VStack({len(self._elements)} elements)>"

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:

        vertical_padding = self._h.value if self._h.mode == SizeMode.FIT else 0

        # Calculate the total height of the elements, and the spacing between them
        total_height_of_elements = 0
        total_element_fill_height = 0
        element_fill_count = 0
        for i in self._elements:
            if i._h.mode == SizeMode.FILL:
                total_element_fill_height += i._h.percentage
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
                        (round(h) - vertical_padding - total_height_of_elements)
                        / (len(self._elements) - 1)
                    ),
                )
        else:
            spacing = self.min_spacing

        remaining_height = (
            h - vertical_padding - total_height_of_elements - spacing * (len(self._elements) - 1)
        )

        # Update own rect
        super()._update_rect_chain_down(surface, x, y, w, h)

        if not self._elements:
            return

        # Find the y position of the first child element
        if total_element_fill_height == 0 and (
            self.spacing is not None or len(self._elements) == 1
        ):
            if self._h.mode == SizeMode.FIT:
                element_y = remaining_height / 2 + vertical_padding / 2
            else:
                print(vertical_padding)
                element_y = self.content_y.get(self, h, total_height_of_elements + spacing * (len(self._elements) - 1))
            element_y += y - self.rect.y
        else:
            element_y = vertical_padding / 2

        # This is used to equally split the remaining size up between elements with a FILL height
        if element_fill_count != 0:
            remainder = remaining_height % element_fill_count
            # The amount of remainder height that is distributed to elements each side of the stack
            remainder_per_side = (
                math.ceil(remainder / 2) if y - self.rect.y > 0 else remainder // 2
            )
            fill_n = -1

        self._first_visible_element = None

        # Iterate over child elements
        with log.size.indent:
            for n, element in enumerate(self._elements):
                # Find the x position of the child element
                element_x_obj = element._x if element._x is not None else self.content_x
                element_x = x + element_x_obj.get(
                    element,
                    w,
                    element.get_abs_width(w - abs(element_x_obj.value)),
                )

                # Find the height of the child element
                if element._h.mode == SizeMode.FILL:
                    fill_n += 1
                    element_h = (
                        remaining_height // total_element_fill_height * element._h.percentage
                        + element._h.value
                    )
                    element_y -= element._h.value / 2
                    if fill_n < remainder_per_side or fill_n >= element_fill_count - (
                        remainder - remainder_per_side
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
                if element._h.mode == SizeMode.FILL:
                    element_y -= element._h.value / 2

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._h.mode == SizeMode.FIT:
            if self._elements:
                total_height = 0
                for i in self.elements:
                    if i._h.mode == SizeMode.FILL:
                        raise ValueError(
                            "Cannot have elements of FILL height inside of a FIT height VStack."
                        )
                    total_height += i.get_abs_height()
                self._min_h = total_height + self.min_spacing * (
                    len(self._elements) - 1
                )
            else:
                self._min_h = 20

        if self._w.mode == SizeMode.FIT:
            if self._elements:
                if any(i._w.mode == SizeMode.FILL for i in self._elements):
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width VStack."
                    )
                self._min_w = max(i.get_abs_width() for i in self._elements)
            else:
                self._min_w = 20

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
