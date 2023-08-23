import pygame
from typing import TYPE_CHECKING, Union, Optional, Sequence

if TYPE_CHECKING:
    from .base.element import Element

from .. import common as _c
from .. import log
from .box import Box


class Section(Box):
    """
    A subclass of Box that can itself be focused when using keyboard / controller navigation.
    """

    def __repr__(self) -> str:
        return "<Section>"

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if direction in {_c.FocusDirection.IN, _c.FocusDirection.IN_FIRST}:
            log.nav.info("Returning self.")
            return self

        if self.layer.element_focused is self:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        if direction == _c.FocusDirection.OUT:
            log.nav.info(f"Returning self.")
            return self
        elif (
            direction
            in {
                _c.FocusDirection.UP,
                _c.FocusDirection.DOWN,
                _c.FocusDirection.LEFT,
                _c.FocusDirection.RIGHT,
                _c.FocusDirection.FORWARD,
            }
            or self._element is None
        ):
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(f"-> child {self._element}.")
            return self._element._focus_chain(direction)

    def _event(self, event: pygame.event.Event) -> bool:
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (
            event.type == pygame.JOYBUTTONDOWN and event.button == 0
        ):
            if self.layer.element_focused is self and self._element is not None:
                with log.nav.indent("Enter key pressed, starting focus chain."):
                    if self._element._can_focus:
                        self.layer.shift_focus(_c.FocusDirection.IN, element=self._element)
                log.nav.info(
                    f"Focus chain ended. Focused {self.layer.element_focused}.", self
                )
                return True

        return super()._event(event)
