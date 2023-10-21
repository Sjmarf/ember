from typing import TYPE_CHECKING, Union

import pygame

from ember.base.element import Element
from ember.event import DISABLED, ENABLED

if TYPE_CHECKING:
    pass
class CanDisable(Element):
    """
    This class is a mixin, and should not be instantiated directly.
    It provides functionality for disabling the element.
    """

    def __init__(self, *args, disabled: bool = False, **kwargs) -> None:
        self._disabled: bool = disabled
        super().__init__(*args, **kwargs)
    
    def _set_disabled(self, value: bool) -> None:
        # Is overriden by subclasses of Interactive to provide extra functionality
        pass

    def set_disabled(self, value: bool) -> None:
        """
        Disabled Elements cannot be interacted with. This method is synonymous with
        the :py:property:`ember.ui.base.Interactive.disabled` property setter.
        """
        if value != self._disabled:
            self._disabled = value
            self._set_disabled(value)
            event = pygame.event.Event(DISABLED if value else ENABLED, element=self)
            self._post_event(event)
            if self.parent is not None:
                self.parent.update_min_size()
            if self._disabled and self.layer is not None:
                if self.layer.element_focused is self:
                    self.layer._focus_element(None)

    @property
    def disabled(self) -> bool:
        """
        Disabled Elements cannot be interacted with. The property setter is synonymous 
        with the :py:meth:`ember.ui.base.Interactive.set_disabled` method.
        """
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self.set_disabled(value)

