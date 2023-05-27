import math
import pygame
from ..common import INHERIT, InheritType
from typing import Union, Optional, Sequence, Literal

from .base.stack import Stack
from .. import log
from ..size import FIT, FILL, SizeType, SequenceSizeType
from ..position import PositionType
from .view import ViewLayer
from .base.element import Element
from ..material.material import Material

from ..style.container_style import ContainerStyle


class VStack(Stack):
    def __init__(
        self,
        *elements: Union[Element, Sequence[Element]],
        background: Optional[Material] = None,
        spacing: Union[InheritType, int] = INHERIT,
        min_spacing: Union[InheritType, int] = INHERIT,
        focus_self: Union[InheritType, bool] = INHERIT,
        align_elements: Union[
            InheritType, Literal["left", "center", "right"]
        ] = INHERIT,
        position: PositionType = None,
        size: SequenceSizeType = None,
        width: SizeType = None,
        height: SizeType = None,
        style: Optional[ContainerStyle] = None,
    ):
        self.layer: Optional[ViewLayer] = None
        self.parent: Optional[Element] = None

        self._elements = []
        self.set_elements(*elements, _supress_update=True)
        super().__init__(
            style,
            background,
            spacing,
            min_spacing,
            focus_self,
            position,
            size,
            width,
            height,
            default_size=(
                FILL if any(i._width.mode == 2 for i in self._elements) else FIT,
                FILL if any(i._height.mode == 2 for i in self._elements) else FIT,
            ),
        )
        self._update_elements()

        self.align_elements: Literal["left", "center", "right"] = (
            self._style.align_elements_v
            if align_elements is INHERIT
            else align_elements
        )

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
        stack_height = self.get_abs_height(max_size[1])
        padding = self._height.value if self._height.mode == 1 else 0

        # Calculate the total height of the elements, and the spacing between them
        height_of_elements = 0
        element_fill_height = 0
        element_fill_count = 0
        for i in self._elements:
            if i._height.mode == 2:
                element_fill_height += i._height.percentage
                element_fill_count += 1
            else:
                height_of_elements += i.get_abs_height()

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
        stack_width = self.get_abs_width(max_size[0])

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
                if self.align_elements == "center":
                    x = (
                        self._draw_rect.x
                        + stack_width // 2
                        - element.get_abs_width(stack_width) // 2
                    )
                elif self.align_elements == "left":
                    x = pos[0]
                else:
                    x = pos[0] + stack_width - element.get_abs_width(self.rect.w)

                if element._height.mode == 2:
                    fill_n += 1
                    h = (
                        remaining_height
                        // element_fill_height
                        * element._height.percentage
                        + element._height.value
                    )
                    y -= element._height.value / 2
                    if fill_n < top_rem or fill_n >= element_fill_count - (
                        remainder - top_rem
                    ):
                        h += 1
                else:
                    h = element.get_abs_height()
                
                if not self.is_visible:
                    element.is_visible = False                
                elif (
                    self._draw_rect.y + y + h <= surface.get_abs_offset()[1]
                    or self._draw_rect.y + y
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
                    max_size=(self.rect.w, h),
                    _ignore_fill_height=True,
                )                

                y += spacing + h
                if element._height.mode == 2:
                    y -= element._height.value / 2

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._height.mode == 1:
            if self._elements:
                total_height = 0
                for i in self.elements:
                    if i._height.mode == 2:
                        raise ValueError(
                            "Cannot have elements of FILL height inside of a FIT height VStack."
                        )
                    total_height += i.get_abs_height()
                self._fit_height = total_height + self.min_spacing * (
                    len(self._elements) - 1
                )
            else:
                self._fit_height = 20

        if self._width.mode == 1:
            if self._elements:
                if any(i._width.mode == 2 for i in self._elements):
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width VStack."
                    )
                self._fit_width = max(i.get_abs_width() for i in self._elements)
            else:
                self._fit_width = 20

    def _focus_chain(self, previous=None, direction: str = "in") -> Element:
        looking_for = self.layer.element_focused if previous is None else previous

        if self.layer.element_focused is self:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(self, direction=direction)

        if direction in {"up", "down", "forward", "backward"}:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = len(self._elements) - 1 if direction == "up" else 0

            if direction in {"up", "backward"}:
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
                    return element._focus_chain(None)

            # If no element is found, return to the parent
            return self.parent._focus_chain(self, direction=direction)

        elif direction in {"left", "right"}:
            log.nav.info(self, f"-> parent {self.parent}.")
            return self.parent._focus_chain(self, direction=direction)

        elif direction == "out":
            if self.focus_self:
                log.nav.info(self, f"Returning self.")
                return self
            else:
                log.nav.info(self, f"-> parent {self.parent}.")
                return self.parent._focus_chain(self, direction=direction)

        else:
            return self._enter_in_first_element(direction)

    def _enter_in_first_element(
        self, direction: str, ignore_self_focus: bool = False
    ) -> Optional[Element]:
        # The stack is being entered, so select the element closest to the previous element
        if self.focus_self and not ignore_self_focus:
            log.nav.info(self, "Returning self.")
            return self

        if (
            (not ignore_self_focus)
            and (self.layer.element_focused is not None)
            and self._style.focus_on_entry == "closest"
            and direction != "in_first"
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

        if direction == "in_first":
            direction = "in"
        return closest_element._focus_chain(None, direction=direction)
