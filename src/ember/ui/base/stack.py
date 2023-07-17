import pygame

from typing import Optional, Sequence, Union, TYPE_CHECKING, Generator

from ember.common import InheritType, INHERIT, FocusType
from ember import log
from ember.ui.base.element import Element
from ember.size import SizeType, OptionalSequenceSizeType
from ember.position import (
    PositionType,
    SequencePositionType,
    Position,
    OptionalSequencePositionType,
)

from ember.state.state_controller import StateController
from ember.state.background_state import BackgroundState

from ember.material.material import Material

from ember.ui.base.multi_element_container import MultiElementContainer
from .has_content_size import ContentSizeMixin

if TYPE_CHECKING:
    from ember.style.container_style import ContainerStyle


class Stack(ContentSizeMixin, MultiElementContainer):
    """
    A Stack is a collection of Elements. There are two subclasses of Stack - :py:class:`ember.ui.VStack`
    and :py:class:`ember.ui.HStack`. This base class should not be instantiated directly.
    """

    def __init__(
        self,
        elements: tuple[
            Union[Element, Sequence[Element], Generator[Element, None, None]]
        ],
        material: Union[BackgroundState, Material, None],
        spacing: Union[InheritType, int],
        min_spacing: Union[InheritType, int],
        focus_on_entry: Union[InheritType, FocusType],
        rect: Union[pygame.rect.RectType, Sequence, None],
        pos: Optional[SequencePositionType],
        x: Optional[PositionType],
        y: Optional[PositionType],
        size: OptionalSequenceSizeType,
        w: Optional[SizeType],
        h: Optional[SizeType],
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
    ):
        """
        The base class for VStack and HStack. Should not be instantiated directly.
        """

        self._first_visible_element: Optional[Element] = None

        super().__init__(
            # MultiElementContainer
            elements=elements,
            material=material,
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
            style=style,
            # ContentSizeMixin
            content_size=content_size,
            content_w=content_w,
            content_h=content_h
        )

        self.spacing: Optional[int] = (
            self._style.spacing if spacing is INHERIT else spacing
        )
        """
        The spacing between the elements. If spacing is set to None, the elements will 
        be spaced evenly the fill the whole Stack. If no spacing is specified, the 
        spacing from the ContainerStyle is used.
        """

        self.min_spacing: int
        """
        The minimum spacing between the elements. Only effective if the 'spacing' attribute is None.
        """

        if self.spacing:
            self.min_spacing = self.spacing
        else:
            self.min_spacing = (
                self._style.min_spacing if min_spacing is INHERIT else min_spacing
            )

        self._total_size_of_nonfill_elements: int = 0
        self._total_size_of_fill_elements: int = 0
        self._fill_element_count: int = 0

    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        for n, i in enumerate(self._elements[self._first_visible_element :]):
            if not i.is_visible:
                break
            i._render_a(surface, offset, alpha=alpha)

    def _update(self) -> None:
        for i in self._elements[self._first_visible_element :]:
            i._update_a()
            if not i.is_visible:
                break

    def _event(self, event: pygame.event.Event) -> bool:
        for i in self._elements[self._first_visible_element :]:
            if i._event(event):
                return True
            if not i.is_visible:
                break
        return False

    def _enter_in_first_element(
        self, key: str, ignore_self_focus: bool = False
    ) -> Optional[Element]:
        pass

    def _get_element_spacing(self, padding: int, is_fit: bool) -> int:
        """Get the spacing between the elements in the Stack"""
        if self.spacing is not None:
            return self.spacing

        elif self._fill_element_count > 0 or is_fit:
            return self.min_spacing

        else:
            if len(self._elements) == 1:
                return 0
            else:
                return max(
                    self.min_spacing,
                    int(
                        (self.rect.w - padding - self._total_size_of_nonfill_elements)
                        / (len(self._elements) - 1)
                    ),
                )
