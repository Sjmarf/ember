import pygame

from typing import Optional, TYPE_CHECKING, NamedTuple
from dataclasses import dataclass

from ember import log
from ember import axis
from ember.axis import HORIZONTAL

from ember import common as _c
from ember.common import (
    SequenceElementType,
    FOCUS_CLOSEST,
    FOCUS_AXIS_FORWARD,
    FOCUS_AXIS_BACKWARD,
    FocusDirection,
)
from ember.ui.element import Element
from .focus_passthrough import FocusPassthroughContainer
from .can_pivot import CanPivot

from ember.trait.trait import Trait
from ember.spacing import SpacingType, FILL_SPACING, load_spacing, Spacing
from ember.size import FillSize, FitSize, AbsoluteSize
from ember.position import CENTER, load_position, PositionType

if TYPE_CHECKING:
    pass


class Grid(FocusPassthroughContainer, CanPivot):
    spacing1 = Trait(
        FILL_SPACING,
        on_update=lambda self: self.update_min_size_next_tick(self),
        load_value_with=load_spacing,
    )

    spacing2 = Trait(
        FILL_SPACING,
        on_update=lambda self: self.update_min_size_next_tick(self),
        load_value_with=load_spacing,
    )

    alignment1 = Trait(
        CENTER,
        on_update=lambda self: self.update_min_size_next_tick(self),
        load_value_with=load_position,
    )

    alignment2 = Trait(
        CENTER,
        on_update=lambda self: self.update_min_size_next_tick(self),
        load_value_with=load_position,
    )

    @dataclass
    class Row:
        max_items: int
        start_index: int
        sizes: tuple[float, ...]

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        spacing: Optional[SpacingType] = None,
        horizontal_spacing: Optional[SpacingType] = None,
        vertical_spacing: Optional[SpacingType] = None,
        alignment1: Optional[PositionType] = None,
        alignment2: Optional[PositionType] = None,
        wrap_length: Optional[int] = None,
        uniform_size_allocation: bool = False,
        **kwargs,
    ):
        self.wrap_length: Optional[int] = wrap_length
        self.uniform_size_allocation: bool = uniform_size_allocation

        self._first_visible_element: Optional[int] = None

        if spacing is not None:
            horizontal_spacing, vertical_spacing = spacing, spacing

        self.spacing2 = horizontal_spacing
        self.spacing1 = vertical_spacing

        self.alignment1 = alignment1
        self.alignment2 = alignment2

        super().__init__(*elements, **kwargs)

    def _get_row_sizes(
        self, elements: list["Element"], spacing: float, max_items_in_row: int
    ) -> Row:
        unallocated_space = (self.rect[3 - self.axis]) - spacing * (
            max_items_in_row - 1
        )

        sizes = []

        for n, element in enumerate(elements):
            element: Element
            max_size = unallocated_space / max(1, (max_items_in_row - n))
            size = element.get_abs_rel_size2(max_size)
            unallocated_space -= size
            if unallocated_space >= 0:
                sizes.append(size)
            else:
                if not sizes:
                    sizes.append(size)
                break
            if len(sizes) == max_items_in_row:
                break

        return Grid.Row(max_items=max_items_in_row, start_index=0, sizes=tuple(sizes))

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        elements = list(self._elements_to_render)
        min_spacing1 = self.spacing1.get_min()
        min_spacing2 = self.spacing2.get_min()

        rows: list[Grid.Row] = []
        start_index = 0

        # Calculate how many items should be on each row, and what their size1s should be
        while True:
            max_items_in_row = (
                self.wrap_length if self.wrap_length is not None else len(elements)
            )
            previous_row_candidate = Grid.Row(max_items=0, start_index=0, sizes=())

            while True:
                row_candidate = self._get_row_sizes(
                    elements[start_index:],
                    spacing=min_spacing2,
                    max_items_in_row=max_items_in_row,
                )
                row_candidate.start_index = start_index
                if max_items_in_row != (len(elements) - start_index) and len(
                    row_candidate.sizes
                ) < len(previous_row_candidate.sizes):
                    break

                previous_row_candidate = row_candidate

                max_items_in_row -= 1
                if max_items_in_row <= 0:
                    break

            rows.append(previous_row_candidate)
            start_index += len(previous_row_candidate.sizes)
            if start_index == len(elements):
                break

        if self.uniform_size_allocation:
            max_items = max(i.max_items for i in rows)
            for i in range(len(rows)):
                if rows[i].max_items != max_items:
                    rows[i] = self._get_row_sizes(
                        elements[
                            rows[i].start_index : rows[i].start_index
                            + len(rows[i].sizes)
                        ],
                        spacing=min_spacing2,
                        max_items_in_row=max_items,
                    )

        # Find the size2 of each element

        elements_iter = iter(elements)
        element_size1s = [
            element.get_abs_rel_size1(self.rect[2 + self.axis]) for element in elements
        ]
        element_size1s_iter = iter(element_size1s)

        # Find the size2s of each row

        row_size1s = []
        start_index = 0
        for row in rows:
            row_size1s.append(
                max(element_size1s[start_index : start_index + len(row.sizes)])
            )
            start_index += len(row.sizes)
        row_size1s_iter = iter(row_size1s)

        unallocated_space = (
            self.rect[2 + self.axis]
            - sum(row_size1s)
            - min_spacing1 * (len(row_size1s) - 1)
        )
        if unallocated_space > 0 and len(row_size1s) > 1:
            spacing1 = self.spacing1.get(
                min_spacing1 + int(unallocated_space / (len(row_size1s) - 1))
            )
        else:
            spacing1 = min_spacing2
        
        
        element_rel_pos1 = self.rect[self.axis] + self.alignment1.get(
            self.rect[2 + self.axis],
            (sum(row_size1s) + spacing1 * (len(row_size1s) - 1)),
            self.axis
            )
        
        del element_size1s, row_size1s

        # Apply the calculated geometry to the child elements

        for row in rows:
            row_size = next(row_size1s_iter)
            
            unallocated_space = (
                self.rect[3 - self.axis]
                - sum(row.sizes)
                - min_spacing2 * (len(row.sizes) - 1)
            )                        
            if unallocated_space > 0 and len(row.sizes) > 1:
                spacing2 = self.spacing2.get(
                    min_spacing2 + int(unallocated_space / (len(row.sizes) - 1))
                )
            else:
                spacing2 = min_spacing2

            element_rel_pos2 = self.rect[1 - self.axis] + self.alignment2.get(
                self.rect[3 - self.axis],
                (sum(row.sizes) + spacing2 * (len(row.sizes) - 1)),
                self.axis,
            )
                                    
            for element_rel_size2 in row.sizes:
                element = next(elements_iter)    
                
                element_rel_size1 = next(element_size1s_iter)
                
                element.update_rect(
                    surface,
                    rel_pos2=element_rel_pos2,
                    rel_pos1=element_rel_pos1 + element.rel_pos1.get(row_size, element_rel_size1, self.axis),
                    rel_size2=element_rel_size2,
                    rel_size1=element_rel_size1,
                )

                element.visible = True
                element_rel_pos2 += element_rel_size2 + spacing2

            element_rel_pos1 += row_size + spacing1

    def _update_min_size(self) -> None:
        # if self._elements:
        #     size = 0
        #     for i in self.elements:
        #         if i is not None:
        #             if not isinstance(i.rel_size1, FillSize):
        #                 size += i.get_abs_rel_size1()

        #     self._min_size[self.axis] = size + self.spacing.get_min() * (
        #         len(self._elements) - 1
        #     )
        #     self._min_size[1-self.axis] = max(
        #         [i.get_abs_rel_size2() for i in self._elements if i is not None]
        #         or (20,)
        #     )
        # else:
        self._min_size.x, self._min_size.y = 20, 20

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        # for n, i in enumerate(self._elements[self._first_visible_element :]):
        for n, i in enumerate(self._elements):
            if not i.visible:
                break
            i.render(surface, offset, alpha=alpha)

    def _update(self) -> None:
        for i in self._elements:
            i.update()
            if not i.visible:
                break

    def _event(self, event: pygame.event.Event) -> bool:
        for i in self._elements:
            if i is None:
                continue
            if i.event(event):
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
            FOCUS_AXIS_BACKWARD[self.axis],
            FOCUS_AXIS_FORWARD[self.axis],
            FocusDirection.FORWARD,
            FocusDirection.BACKWARD,
        }:
            # Select next/previous element in the stack
            if looking_for in self._elements:
                index = self._elements.index(looking_for)
            else:
                index = (
                    len(self._elements) - 1
                    if direction == FOCUS_AXIS_FORWARD[self.axis]
                    else 0
                )

            if direction in {
                FOCUS_AXIS_FORWARD[self.axis],
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
                self.layer.element_focused.rect[self.axis]
                + self.layer.element_focused.rect[2 + self.axis] / 2
            )
            closest_elements = sorted(
                self._elements,
                key=lambda x: abs(
                    x.rect[self.axis] + x.rect[2 + self.axis] / 2 - comparison
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
        return closest_element.focus_chain(_c.FocusDirection.IN)
