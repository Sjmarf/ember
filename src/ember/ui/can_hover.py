from typing import TYPE_CHECKING

from ember.ui.element import Element
from ember.event import HOVERED, UNHOVERED

from ember import common as _c

if TYPE_CHECKING:
    pass


class CanHover(Element):
    def __init__(self, *args, **kwargs) -> None:
        self._hovered: bool = False
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
