import pygame
from abc import ABC
from typing import Optional, Sequence, Union, TypeVar, Generic, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .multi_element_container import MultiElementContainer

from ember import log

from ember.common import ElementType
from .context_manager import ContextManager
from .container import Container


from .element import Element


class SingleElementContainer(ContextManager, Container, ABC):
    
    multi_element_wrapper: type["MultiElementContainer"] | None = None

    def __init__(self, element: Optional["Element"] = None, **kwargs):
        """
        Base class for Containers that hold one or zero elements. Should not be instantiated directly.
        """

        self._element: Optional["Element"] = None

        super().__init__(**kwargs)

        self.set_element(element, _update=False)

    def __getitem__(self, item: int) -> "Element":
        if item == 0:
            return self._element
        else:
            return NotImplemented

    def __setitem__(self, key: int, value: "Element"):
        if key != 0 or not isinstance(value, Element):
            return NotImplemented

        self.set_element(value)

    def __delitem__(self, key: int):
        if key != 0:
            raise ValueError
        if self._element is not None:
            self.removing_element(self._element)
            self._element = None

    def _attribute_elements(self, elements: Sequence[Element]) -> None:
        if len(elements) == 1:
            self.set_element(elements[0], _update=False)       
        elif self.multi_element_wrapper is not None:
            self.set_element(self.multi_element_wrapper(elements), _update=False)
        else:
            raise ValueError(f"f{self} can only contain one element, but you tried to add more than one.")

    @property
    def element(self) -> Optional[Element]:
        return self._element

    @element.setter
    def element(self, element: Optional[Element]) -> None:
        self.set_element(element)

    @property
    def _elements_to_render(self) -> Iterable[Element]:
        return (self._element,)

    def set_element(
        self,
        element: Optional["Element"],
        _update: bool = True,
    ) -> None:
        """
        Replace the element in the Container with a new element.
        """
        
        with log.ancestry.indent(f"SET {self}, {element}"):
            if element is not self._element:
                self.removing_element(self._element,update=_update)
                with self.adding_element(element, update=_update) as element:
                    self._element = element


    def remove_child(self, element: Element) -> None:
        if element is self._element:
            self.set_element(None)
        else:
            raise ValueError(f"Tried to remove child element {element} from container {self}, but it was not a child.")