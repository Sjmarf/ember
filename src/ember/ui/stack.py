from typing import Optional, TYPE_CHECKING

from ember import log

from ember import common as _c
from ember.common import (
    SequenceElementType,
    FOCUS_CLOSEST,
    FOCUS_AXIS_FORWARD,
    FOCUS_AXIS_BACKWARD,
    FocusDirection,
)
from ember.ui.element import Element
from ember.ui.has_geometry import HasGeometry
from .focus_passthrough import FocusPassthroughContainer
from .can_pivot import CanPivot
from .geometric_container import GeometricContainer, LayoutBlueprint, LayoutPlacement

from ember.trait.trait import Trait
from ember.spacing import SpacingType, FILL_SPACING, load_spacing
from ember.utility.geometry_vector import GeometryVector
from ember.utility.geometry_rect import GeometryRect

if TYPE_CHECKING:
    pass


class Stack(FocusPassthroughContainer, CanPivot, GeometricContainer):
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
        self._first_visible_element: Optional[int] = None
        self.spacing = spacing
        super().__init__(*elements, **kwargs)

    def get_layout_blueprint(
        self, elements: tuple[HasGeometry, ...], proposed_size: GeometryVector
    ) -> LayoutBlueprint:
        proposed_size.axis = self.axis
        space_count = len(elements) - 1

        total_size = GeometryVector(0, 0, axis=self.axis)
        spacing = self.spacing.get_min()
        unallocated_depth = proposed_size.depth - spacing * space_count

        element_sizes: dict[HasGeometry, GeometryVector] = {}

        def determine_flexibility(el: HasGeometry) -> float:
            maximum = el.get_dimensions(
                GeometryVector(
                    breadth=proposed_size.breadth,
                    depth=proposed_size.depth,
                    axis=self.axis
                ),
            ).depth
            minimum = el.get_dimensions(
                GeometryVector(
                    breadth=proposed_size.breadth,
                    depth=1,
                    axis=self.axis
                ),
            ).depth
            return maximum-minimum

        for n, element in enumerate(
            sorted(elements, key=determine_flexibility)
        ):
            proposal = proposed_size.copy()
            if proposal.depth != 0:
                proposal.depth = unallocated_depth / (len(elements) - n)
            element_size = element.get_dimensions(proposal)

            element_sizes[element] = element_size
            total_size.depth += element_size.depth
            total_size.breadth = max(total_size.breadth, element_size.breadth)
            unallocated_depth -= element_size.depth

        if unallocated_depth > 0 and len(elements) > 1:
            spacing = self.spacing.get(spacing + int(unallocated_depth / space_count))

        cursor = (
            proposed_size.depth / 2 - (total_size.depth + spacing * space_count) / 2
        )
        total_size.depth += spacing * space_count

        if proposed_size.w != 0:
            total_size.w = proposed_size.w
        if proposed_size.h != 0:
            total_size.h = proposed_size.h

        placements: list[LayoutPlacement] = []
        for element in elements:
            element_size = element_sizes[element]
            element_origin = GeometryVector(
                depth=cursor,
                breadth=element.rel_pos2.get(
                    proposed_size.breadth, element_size.breadth
                ),
                axis=self.axis,
            )
            placement = LayoutPlacement(
                element, GeometryRect(origin=element_origin, size=element_size)
            )
            placements.append(placement)
            cursor += element_size.depth + spacing

        return LayoutBlueprint(size=total_size, placements=placements)

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
