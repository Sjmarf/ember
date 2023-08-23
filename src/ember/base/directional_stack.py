import pygame

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from ember import log

from ember.common import SequenceElementType
from ember.base.element import Element
from .stack import Stack

from ember.trait import new_trait
from ember.spacing import Spacing, SpacingType, load_spacing, DEFAULT_SPACING

from ..base.content_pos_direction import PerpendicularContentPos
from ..base.content_size_direction import DirectionalContentSize

if TYPE_CHECKING:
    pass


class DirectionalStack(PerpendicularContentPos, DirectionalContentSize, Stack, ABC):
    """
    A Stack is a collection of Elements. There are two subclasses of DirectionalStack - :py:class:`ember.ui.VStack`
    and :py:class:`ember.ui.HStack`. This base class should not be instantiated directly.
    """

    spacing, spacing_ = new_trait(
        DEFAULT_SPACING, on_update=lambda self: self.update_min_size_next_tick(self)
    )

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        spacing: Optional[SpacingType] = None,
        **kwargs,
    ):
        self._first_visible_element: Optional[Element] = None

        self.spacing = load_spacing(spacing)

        self._total_size_of_nonfill_elements: int = 0
        self._total_size_of_fill_elements: int = 0
        self._fill_element_count: int = 0

        super().__init__(
            # MultiElementContainer
            *elements,
            **kwargs,
        )

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        for n, i in enumerate(self._elements[self._first_visible_element :]):
            if not i.visible:
                break
            i.render(surface, offset, alpha=alpha)

    def _update(self) -> None:
        for i in self._elements[self._first_visible_element :]:
            i.update()
            if not i.visible:
                break

    def _event(self, event: pygame.event.Event) -> bool:
        for i in self._elements[self._first_visible_element :]:
            if i._event(event):
                return True
            if not i.visible:
                break
        return False

    @abstractmethod
    def _enter_in_first_element(
        self, key: str, ignore_self_focus: bool = False
    ) -> Optional[Element]:
        pass

    def update_can_focus(self) -> None:
        if self in self.layer.can_focus_update_queue:
            self.layer.can_focus_update_queue.remove(self)

        if self._can_focus != any(i._can_focus for i in self._elements):
            self._can_focus = not self._can_focus
            log.nav.info(f"Changed can_focus to {self._can_focus}.", self)
            if self.parent is not None:
                self.parent.update_can_focus()
        else:
            log.nav.info(
                f"can_focus remained {self._can_focus}, cutting chain...", self
            )

    def _get_element_spacing(self, size: float, padding: int, is_fit: bool) -> int:
        """
        Get the spacing between the elements in the Stack
        """

        if len(self._elements) == 1:
            return 0

        if self._fill_element_count > 0 or is_fit:
            return self.spacing.get_min()

        return self.spacing.get(
            int(
                (size - padding - self._total_size_of_nonfill_elements)
                / (len(self._elements) - 1)
            ),
        )
