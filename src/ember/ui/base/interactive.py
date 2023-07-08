from typing import TYPE_CHECKING, Union

from .element import Element

if TYPE_CHECKING:
    pass


class Interactive:
    """
    This class is a secondary superclass of elements that are interactive.
    It provides functionality for disabling the element.
    """

    def __init__(self: "InteractiveElement", disabled: bool) -> None:
        self._disabled: bool = disabled
    
    def _set_disabled(self: "InteractiveElement", value: bool) -> None:
        # Is overriden by subclasses of Interactive to provide extra functionality
        pass

    def set_disabled(self: "InteractiveElement", value: bool) -> None:
        """
        Disabled Elements cannot be interacted with. This method is synonymous with
        the :py:property:`ember.ui.base.Interactive.disabled` property setter.
        """
        self._disabled = value
        self._can_focus = not value
        self._set_disabled(value)
        if self.parent is not None:
            self.parent._update_rect_chain_up()
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


InteractiveElement = Union[Element, Interactive]
