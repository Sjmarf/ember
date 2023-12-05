from typing import TYPE_CHECKING, Self, Optional
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from ember.ui.element import Element

# DON'T make this inherit from Element - View uses this
class ContextManager(ABC):
    """
    Represents an element or View that supports context management.
    """

    context_stack: list[Optional["ContextManager"]] = [None]
    """
    LIFO. Holds the elements that we are currently in the context of.
    """

    def __init__(self, *args, **kwargs):
        self.context_queue: list["Element"] = []
        """
        FIFO. Holds the elements that have been instantiated in this context.
        """
        super().__init__(*args, **kwargs)

    def __enter__(self) -> Self:
        self.context_stack.append(self)
        self.context_queue.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context_stack.pop()
        
        # Only attribute elements that aren't already attributed to an element.
        for element in self.context_queue:
            if element.parent is None:
                self._attribute_element(element)
        self.context_queue.clear()

    @abstractmethod
    def _attribute_element(self, element: "Element") -> None:
        pass

