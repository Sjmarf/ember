import math
import pygame
from .. import common as _c
from ..common import INHERIT, InheritType, FocusType, FOCUS_CLOSEST, FOCUS_FIRST
from typing import Union, Optional, Sequence, Literal, TYPE_CHECKING

from .base.stack import Stack
from .. import log
from ..size import FIT, FILL, SizeType, SequenceSizeType, SizeMode
from ..position import PositionType, CENTER, SequencePositionType, Position
from .view import ViewLayer
from .base.element import Element
from ..material.material import Material
from ..state.state import State

if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle


class HStack(Stack):
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

        self.align: Position = self._style.align[1] if align is INHERIT else align

        self._update_elements()

    def __repr__(self) -> str:
        return f"<HStack({len(self._elements)} elements)>"

    def _update_rect_chain_down(
        self,
        surface: pygame.Surface,
        pos: tuple[float, float],
        max_size: tuple[float, float],
        _ignore_fill_width: bool = False,
        _ignore_fill_height: bool = False,
    ) -> None:
        # Calculate own width
        stack_width = self.get_ideal_width(max_size[0])
        padding = self._w.value if self._w.mode == SizeMode.FIT else 0

        # Calculate the total width of the elements, and the spacing between them
        width_of_elements = 0
        element_fill_width = 0
        element_fill_count = 0
        for i in self._elements:
            if i._w.mode == SizeMode.FILL:
                element_fill_width += i._w.percentage
                element_fill_count += 1
            else:
                width_of_elements += i.get_ideal_width()

        if self.spacing is not None:
            spacing = self.spacing

        elif element_fill_width == 0:
            if len(self._elements) == 1:
                spacing = 0
            else:
                spacing = max(
                    self.min_spacing,
                    int(
                        (round(stack_width) - padding - width_of_elements)
                        / (len(self._elements) - 1)
                    ),
                )
        else:
            spacing = self.min_spacing

        remaining_width = (
            round(stack_width)
            - padding
            - width_of_elements
            - spacing * (len(self._elements) - 1)
        )

        # Update own width and height
        stack_height = self.get_ideal_height(max_size[1])

        super()._update_rect_chain_down(surface, pos, max_size)

        # Update width and height of elements
        if not self._elements:
            return

        if element_fill_width == 0 and (
            self.spacing is not None or len(self._elements) == 1
        ):
            x = remaining_width / 2 + padding / 2
            # x += pos[0] - self._draw_rect.x
        else:
            x = padding / 2

        if element_fill_count:
            remainder = remaining_width % element_fill_count
            left_rem = (
                math.ceil(remainder / 2) if pos[0] - self.rect.x > 0 else remainder // 2
            )
            fill_n = -1

        self._first_visible_element = None

        with log.size.indent:
            for n, element in enumerate(self._elements):
                element_y = element._y if element._y is not None else self.align

                y = pos[1] + element_y.get(
                    element,
                    stack_height,
                    element.get_ideal_height(stack_height - abs(element_y.value)),
                )

                if element._w.mode == SizeMode.FILL:
                    fill_n += 1
                    w = (
                        remaining_width
                        // element_fill_width
                        * element._w.percentage
                        + element._w.value
                    )
                    x -= element._w.value / 2
                    if fill_n < left_rem or fill_n >= element_fill_count - (
                        remainder - left_rem
                    ):
                        w += 1
                else:
                    w = element.get_ideal_width()

                if not self.is_visible:
                    element.is_visible = False
                elif (
                    self.rect.x + x + w < surface.get_abs_offset()[0]
                    or self.rect.x + x
                    > surface.get_abs_offset()[0] + surface.get_width()
                ):
                    element.is_visible = False
                else:
                    element.is_visible = True
                    if self._first_visible_element is None:
                        self._first_visible_element = n

                element._update_rect_chain_down(
                    surface,
                    (self._int_rect.x + x, y),
                    max_size=(w, self.rect.h - abs(element_y.value)),
                    _ignore_fill_width=True,
                )

                x += spacing + w
                if element._w.mode == SizeMode.FILL:
                    x -= element._w.value / 2

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._w.mode == SizeMode.FIT:
            if self._elements:
                total_width = 0
                for i in self.elements:
                    if i._w.mode == SizeMode.FILL:
                        raise ValueError(
                            "Cannot have elements of FILL width inside of a FIT width HStack."
                        )
                    total_width += i.get_ideal_width()
                self._fit_width = total_width + self.min_spacing * (
                    len(self._elements) - 1
                )
            else:
                self._fit_width = 20

        if self._h.mode == SizeMode.FIT:
            if self._elements:
                if any(i._h.mode == SizeMode.FILL for i in self._elements):
                    raise ValueError(
                        "Cannot have elements of FILL height inside of a FIT height HStack."
                    )
                self._fit_height = max(i.get_ideal_height() for i in self._elements)
            else:
                self._fit_height = 20

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
