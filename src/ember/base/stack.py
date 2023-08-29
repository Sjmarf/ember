from typing import Optional
from abc import ABC

from ember import log
from ember.common import (
    FocusType,
    FOCUS_CLOSEST,
)
from ember.base.multi_element_container import MultiElementContainer
from ember.trait import Trait


class Stack(MultiElementContainer, ABC):

    focus_on_entry_: Trait[FocusType] = Trait(FOCUS_CLOSEST)
    focus_on_entry: FocusType = focus_on_entry_.value_descriptor()

    def __init__(self, *args, focus_on_entry: Optional[FocusType] = None, **kwargs):
        self.focus_on_entry = focus_on_entry
        """
        Whether the closest or first element of the container should be focused when the container is entered.
        """

        super().__init__(*args, **kwargs)

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
