import pygame
from abc import ABC
from typing import Optional, Sequence, Union, TypeVar, Generic, Iterable

from ember import log

from ember.common import ElementType
from .context_manager import ContextManager
from .container import Container


from .element import Element

T = TypeVar("T", bound=ElementType, covariant=True)


class SingleElementContainer(Generic[T], ContextManager, Container, ABC):
    def __init__(self, element: Optional[T] = None, **kwargs):
        """
        Base class for Containers that hold one or zero elements. Should not be instantiated directly.
        """

        self._element: Optional[T] = None

        super().__init__(**kwargs)

        self.set_element(element, _update=False)

    def __getitem__(self, item: int) -> T:
        if item == 0:
            return self._element
        else:
            return NotImplemented

    def __setitem__(self, key: int, value: T):
        if key != 0 or not isinstance(value, Element):
            return NotImplemented

        self.set_element(value)

    def __delitem__(self, key: int):
        if key != 0:
            raise ValueError
        if self._element is not None:
            self.removing_element(self._element)
            self._element = None

    def _attribute_element(self, element: T) -> None:
        if self._element is None:
            self.set_element(element, _update=False)
        else:
            raise ValueError(
                "Tried to attribute an element to the container using a `with` statement when it already had an element."
            )

    @property
    def element(self) -> Optional[T]:
        return self._element

    @element.setter
    def element(self, element: Optional[T]) -> None:
        self.set_element(element)

    @property
    def _elements_to_render(self) -> Iterable[Element]:
        return (self._element,)

    def set_element(
        self,
        element: Optional[T],
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
