from typing import TYPE_CHECKING, Union, TypeVar

from .element import Element

if TYPE_CHECKING:
    pass

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


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
        Disabled Elements cannot be interacted with.
        """
        self._disabled = value
        self._can_focus = not value
        self._set_disabled(value)
        if self.parent is not None:
            self.parent._update_rect_chain_up()
        if self._disabled and self.layer is not None:
            if self.layer.element_focused is self:
                self.layer._focus_element(None)

    disabled: bool = property(
        fget=lambda self: self._disabled,
        fset=lambda self, value: self.set_disabled(value),  # noqa
        doc="Disabled Elements cannot be interacted with.",
    )


InteractiveElement = Union[Element, Interactive]
