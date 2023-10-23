from typing import TYPE_CHECKING, Optional, Generator
from abc import ABC, abstractmethod
from contextlib import contextmanager
import pygame

from ember.common import ElementType
from ember.ui.element import Element
from ember.event import FOCUSED, UNFOCUSED

from ember import axis
from ember import common as _c
from ember.ui.container import Container
from ember import log

if TYPE_CHECKING:
    pass

class CanHandleFocus(Element):
    can_handle_focus: bool = True

    def focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        prev_axis = axis.axis
        axis.axis = self._axis
        result = self._focus_chain(direction, previous)
        axis.axis = prev_axis
        return result

    @abstractmethod
    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        ...


class CanHandleFocusChildDependent(CanHandleFocus, Container, ABC):
    @abstractmethod
    def update_can_focus(self) -> None:
        """
        Update the can_handle_focus attribute of the container.
        """

    def _build(self) -> None:
        self.layer.can_focus_update_queue.append(self)
        super()._build()

    @contextmanager
    def adding_element(
        self, element: ElementType, update: bool = True
    ) -> Generator[Optional["Element"], None, None]:
        with super().adding_element(element, update) as element:
            yield element

        if self._has_built and update:
            if self not in self.layer.can_focus_update_queue:
                self.layer.can_focus_update_queue.append(self)

    def removing_element(
        self, element: Optional["Element"], update: bool = True
    ) -> None:
        super().removing_element(element, update)
        if self._has_built and update:
            if self not in self.layer.can_focus_update_queue:
                self.layer.can_focus_update_queue.append(self)


class CanFocus(CanHandleFocus):
    """
    This class is a mixin, and should not be instantiated directly.
    It provides functionality for disabling the element.
    """

    def __init__(self, *args, can_focus: bool = False, **kwargs):
        super().__init__(*args, **kwargs, can_focus=True)

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        # 'previous' is used for going back up the chain - it is set to None when going downwards

        if direction in {
            _c.FocusDirection.IN,
            _c.FocusDirection.IN_FIRST,
            _c.FocusDirection.SELECT,
        }:
            log.nav.info("Returning self.")
            return self
        elif self.parent is not None:
            # Go up a level and try again
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent.focus_chain(direction, previous=self)

    def focus(self) -> None:
        """
        Focuses the element. Only works if the element is inside a ViewLayer.
        """
        if self.layer:
            if self.layer.element_focused is not self:
                self.layer.element_focused = self
                event = pygame.event.Event(FOCUSED, element=self)
                self._post_event(event)
                if not self.visible:
                    self.parent.make_visible(self)
        else:
            raise _c.Error(
                f"Cannot focus {self} because element is not inside of a ViewLayer."
            )

    def unfocus(self) -> None:
        """
        Unfocuses the element.
        """
        if self.layer:
            if self.layer.element_focused is self:
                self.layer.element_focused = None
                event = pygame.event.Event(UNFOCUSED, element=self)
                self._post_event(event)
        else:
            raise _c.Error(
                f"Cannot unfocus {self} because element is not inside of a ViewLayer."
            )

    @property
    def focused(self) -> bool:
        if self.layer is None:
            return False
        return self.layer.element_focused is self

    @focused.setter
    def focused(self, value: bool) -> None:
        if value:
            self.focus()
        else:
            self.unfocus()
