from typing import TYPE_CHECKING, Union

import pygame

from ember.base.element import Element
from ember.event import HOVERED, UNHOVERED

from ember import common as _c

if TYPE_CHECKING:
    pass


class CanHover(Element):
    """
    This class is a mixin, and should not be instantiated directly.
    It provides functionality for disabling the element.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._hovered: bool = False
        """
        Is :code:`True` when the mouse is hovered over the element. Read-only.
        """
        super().__init__(*args, **kwargs)

    def _update(self) -> None:
        if (hovered := self.rect.collidepoint(_c.mouse_pos)) != self._hovered:
            self._hovered = hovered
            if hovered:
                self._post_event(HOVERED)
            else:
                self._post_event(UNHOVERED)

        super()._update()

    @property
    def hovered(self) -> bool:
        return self._hovered
