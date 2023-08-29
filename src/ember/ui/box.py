import pygame
from typing import Optional, TYPE_CHECKING, TypeVar

from ember.base.single_element_container import SingleElementContainer
from ..base.element import Element

if TYPE_CHECKING:
    pass

from .. import common as _c
from ..common import ElementType
from .. import log


T = TypeVar("T", bound=ElementType, covariant=True)

class Box(SingleElementContainer[T]):
    """
    A Box is a container that can optionally hold one Element.
    """

    def __repr__(self) -> str:
        return "<Box>"

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if self.layer.element_focused is self:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        if direction == _c.FocusDirection.OUT:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)
        elif (
            direction
            in {
                _c.FocusDirection.LEFT,
                _c.FocusDirection.RIGHT,
                _c.FocusDirection.UP,
                _c.FocusDirection.DOWN,
                _c.FocusDirection.FORWARD,
            }
            or self._element is None
        ):
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(f"-> child {self._element}.")
            return self._element._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        if self._element is not None:
            return self._element._event(event)
        return False

    def update_can_focus(self) -> None:
        if self in self.layer.can_focus_update_queue:
            self.layer.can_focus_update_queue.remove(self)
        if self._can_focus != (v := self._element and self._element._can_focus):
            self._can_focus = v
            log.nav.info(f"Changed can_focus to {self._can_focus}.", self)
            if self.parent is not None:
                self.parent.update_can_focus()
        else:
            log.nav.info(f"can_focus remained {self._can_focus}, cutting chain...", self)
