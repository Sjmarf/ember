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
        align: Union[InheritType, Position] = INHERIT,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
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

        self.align: Position = self._style.align[0] if align is INHERIT else align

    def __repr__(self) -> str:
        return f"<VStack({len(self._elements)} elements)>"

    def _update_rect_chain_down(
        self,
        surface: pygame.Surface,
        pos: tuple[float, float],
        max_size: tuple[float, float],
        _ignore_fill_width: bool = False,
        _ignore_fill_height: bool = False,
    ) -> None:
        # Calculate own height
        stack_height = self.get_ideal_height(max_size[1])
        padding = self._h.value if self._h.mode == SizeMode.FIT else 0

        # Calculate the total height of the elements, and the spacing between them
        height_of_elements = 0
        element_fill_height = 0
        element_fill_count = 0
        for i in self._elements:
            if i._h.mode == SizeMode.FILL:
                element_fill_height += i._h.percentage
                element_fill_count += 1
            else:
                height_of_elements += i.get_ideal_height()

        if self.spacing is not None:
            spacing = self.spacing

        elif element_fill_height == 0:
            if len(self._elements) == 1:
                spacing = 0
            else:
                spacing = max(
                    self.min_spacing,
                    int(
                        (round(stack_height) - padding - height_of_elements)
                        / (len(self._elements) - 1)
                    ),
                )
        else:
            spacing = self.min_spacing

        remaining_height = (
            stack_height
            - padding
            - height_of_elements
            - spacing * (len(self._elements) - 1)
        )

        # Update own width and height
        stack_width = self.get_ideal_width(max_size[0])

        super()._update_rect_chain_down(surface, pos, max_size)

        # Update width and height of elements
        if not self._elements:
            return

        if element_fill_height == 0 and (
            self.spacing is not None or len(self._elements) == 1
        ):
            y = remaining_height / 2 + padding / 2
            y += pos[1] - self.rect.y
        else:
            y = padding / 2

        if element_fill_count:
            remainder = remaining_height % element_fill_count
            top_rem = (
                math.ceil(remainder / 2) if pos[1] - self.rect.y > 0 else remainder // 2
            )
            fill_n = -1

        self._first_visible_element = None

        with log.size.indent:
            for n, element in enumerate(self._elements):
                element_x = element._x if element._x is not None else self.align
                x = pos[0] + element_x.get(
                    element,
                    stack_width,
                    element.get_ideal_width(stack_width - abs(element_x.value)),
                )

                if element._h.mode == SizeMode.FILL:
                    fill_n += 1
                    h = (
                        remaining_height
                        // element_fill_height
                        * element._h.percentage
                        + element._h.value
                    )
                    y -= element._h.value / 2
                    if fill_n < top_rem or fill_n >= element_fill_count - (
                        remainder - top_rem
                    ):
                        h += 1
                else:
                    h = element.get_ideal_height()

                if not self.is_visible:
                    element.is_visible = False
                elif (
                    self._int_rect.y + y + h <= surface.get_abs_offset()[1]
                    or self._int_rect.y + y
                    >= surface.get_abs_offset()[1] + surface.get_height()
                ):
                    element.is_visible = False
                else:
                    element.is_visible = True
                    if self._first_visible_element is None:
                        self._first_visible_element = n

                element._update_rect_chain_down(
                    surface,
                    (x, self.rect.y + y),
                    max_size=(self.rect.w - abs(element_x.value), h),
                    _ignore_fill_height=True,
                )

                y += spacing + h
                if element._h.mode == SizeMode.FILL:
                    y -= element._h.value / 2

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
                    total_height += i.get_ideal_height()
                self._fit_height = total_height + self.min_spacing * (
                    len(self._elements) - 1
                )
            else:
                self._fit_height = 20

        if self._w.mode == SizeMode.FIT:
            if self._elements:
                if any(i._w.mode == SizeMode.FILL for i in self._elements):
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width VStack."
                    )
                self._fit_width = max(i.get_ideal_width() for i in self._elements)
            else:
                self._fit_width = 20

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
