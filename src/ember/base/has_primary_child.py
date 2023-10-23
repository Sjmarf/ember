from typing import TYPE_CHECKING, Union, Optional, Sequence, Generator
import pygame

from ..common import SequenceElementType, DEFAULT

from ember.base.multi_element_container import MultiElementContainer
from ember.event import CLICKEDDOWN, CLICKEDUP

from ember import common as _c

if TYPE_CHECKING:
    pass


class HasPrimaryChild(MultiElementContainer):
    """
    This class is a mixin, and should not be instantiated directly.
    It provides functionality for clicking an element.
    """
    
    def __init__(self, *args, **kwargs) -> None:
        self.primary_element_index: int = -1
        """
        The index of the element that is considered the 'main' child element of the button.
        """
        super().__init__(*args, **kwargs)  
        
    @property
    def element(self) -> Optional["Element"]:
        return self._elements[self.primary_element_index]

    @element.setter
    def element(self, *element: Optional[SequenceElementType]) -> None:
        self.set_element(*element)

    def set_element(
        self,
        *element: Optional[SequenceElementType],
        _update: bool = True,
    ) -> None:
        """
        Replace the child element of the Button.
        """

        if element:
            if not isinstance(element[0], str) and isinstance(
                element[0], (Sequence, Generator)
            ):
                element = list(element[0])
                if not element:
                    element = (None,)

        else:
            element = (None,)

        if (
            len(self._elements) <= self.primary_element_index or element[0] is not self._elements[self.primary_element_index]
            or len(element) > 1
        ):
            if len(element) > 1:
                element = HStack(element)
            else:
                element = element[0]

            with self.adding_element(element):
                if len(self._elements) <= self.primary_element_index:
                    self._elements.append(element)
                else:
                    self._elements[self.primary_element_index] = element
