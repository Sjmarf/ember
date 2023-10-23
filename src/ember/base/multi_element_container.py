import pygame
from abc import ABC
import copy
from typing import Optional, Sequence, Union, Generator, TYPE_CHECKING, Iterable

from ember.common import (
    ElementType,
    SequenceElementType,
)
from ember import log
from ember.base.element import Element

from ember.size import FillSize

from .container import Container

from ember.trait.trait import Trait
from ember.trait.cascading_trait_value import CascadingTraitValue

if TYPE_CHECKING:
    pass


class MultiElementContainer(Container, ABC):
    def __init__(self, *elements: Optional[SequenceElementType], **kwargs):
        """
        Base class for Containers that hold more than one element. Should not be instantiated directly.
        """

        self.layer = None
        self._elements: list[Optional[Element]] = []

        super().__init__(**kwargs)

        if elements:
            if not isinstance(elements[0], str):
                if isinstance(elements[0], Generator):
                    elements = elements[0]
                elif isinstance(elements[0], Iterable):
                    elements = list(elements[0])
        for element in elements:
            self.append(element, update=False)

    def __getitem__(self, item: int) -> Optional[Element]:
        if isinstance(item, int):
            return self._elements[item]
        else:
            return NotImplemented

    def __setitem__(self, key: int, value: Optional[ElementType]):
        if not isinstance(key, int) or not isinstance(value, (Element, str)):
            return NotImplemented

        self.removing_element(self._elements[key], update=False)
        with self.adding_element(value) as element:
            self._elements[key] = element

    def __delitem__(self, key: int):
        self.removing_element(self._elements[key], update=False)
        del self._elements[key]

    def __len__(self) -> int:
        return len(self._elements)

    def __contains__(self, item: Optional[Element]) -> bool:
        return item in self._elements_to_render

    def _build(self) -> None:
        with Trait.inspecting(Trait.Layer.PARENT), log.size.indent():
            for element in self._elements_to_render:
                if element is not None:
                    self._prepare_element(element)
                    element.build()
        super()._build()

    def _prepare_element(self, element: Element) -> None:
        for value in self.cascading:
            self.start_cascade(value)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        for i in self._elements_to_render:
            if i is not None:
                i.render(surface, offset, alpha=alpha)

    def _update(self) -> None:
        super()._update()
        for i in self._elements_to_render:
            if i is not None:
                i.update()

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        for element in self._elements_to_render:
            if element is None:
                continue
            
            element_w = element.get_abs_w(w, element._axis)
            element_h = element.get_abs_h(h, element._axis)

            element_x = x + element.x.get(w, element_w, element._axis)
            element_y = y + element.y.get(h, element_h, element._axis)
            element.visible = self.visible
            element.update_rect(surface, element_x, element_y, element_w, element_h)

    def _update_min_size(self) -> None:
        self._min_w = 0
        for i in self._elements_to_render:
            if i is None or isinstance(i.w, FillSize):
                continue
            if (w := i.get_abs_w()) > self._min_w:
                self._min_w = w

        self._min_h = 0
        for i in self._elements_to_render:
            if i is None or isinstance(i.h, FillSize):
                continue
            if (h := i.get_abs_h()) > self._min_h:
                self._min_h = h

    def _event(self, event: pygame.event.Event) -> bool:
        for i in self._elements_to_render:
            if i is not None and i._event(event):
                return True
        return super()._event(event)

    def update_ancestry(self, ancestry: list["Element"]) -> None:
        super().update_ancestry(ancestry)
        child_ancestry = self.ancestry + [self]
        with log.ancestry.indent():
            [i.update_ancestry(child_ancestry) for i in self._elements_to_render if i is not None]

    def update_cascading_value(self, value: CascadingTraitValue, depth: int) -> None:
        if value.ref in self.cascading:
            return
        super().update_cascading_value(value, depth)
        depth -= 1
        if depth == 0:
            return
        with log.cascade.indent():
            for element in self._elements_to_render:
                element.update_cascading_value(value, depth)

    def start_cascade(self, value: CascadingTraitValue) -> None:
        with log.cascade.indent(f"Starting descent for {value}", self):
            with Trait.inspecting(Trait.Layer.PARENT):
                value.prepare_for_descent(self)
                for element in self._elements_to_render:
                    element.update_cascading_value(value, value.depth)
        log.cascade.line_break()

    def set_elements(
        self,
        *elements: Optional[SequenceElementType],
        update: bool = True,
    ) -> None:
        """
        Replace the elements in the stack with new elements.
        """
        if elements:
            if isinstance(elements[0], Generator):
                elements = elements[0]
            elif isinstance(elements[0], Sequence):
                elements = list(elements[0])

        if self.layer is not None:
            if (
                self.layer.element_focused in self._elements
                and self.layer.element_focused not in elements
            ):
                self.layer._focus_element(None)

        for element in self._elements:
            self.removing_element(element, update=False)
        self._elements.clear()
        for i in elements:
            with self.adding_element(i, update=False) as element:
                self._elements.append(element)

        if update:
            self.update_min_size_next_tick()

    def _attribute_element(self, element: "Optional[Element]") -> None:
        self.append(element, update=False)

    def append(self, element: Optional[ElementType], update: bool = True) -> None:
        """
        Append an element to the end of the stack.
        """
        with log.ancestry.indent(f"SET {self}, {element}"):
            with self.adding_element(element, update) as element:
                self._elements.append(element)

    def insert(
        self, index: int, element: Optional[ElementType], update: bool = True
    ) -> None:
        """
        Insert an element before at an index.
        """
        with self.adding_element(element, update) as element:
            self._elements.insert(index, element)

    def pop(self, index: int = -1, update: bool = True) -> Optional[Element]:
        """
        Remove and return an element at an index (default last).
        """
        element = self._elements[index]
        self.removing_element(element, update)
        del self._elements[index]
        return element

    def remove(self, element: Optional[Element], update: bool = True) -> None:
        """
        Remove an element from the stack.
        """
        self.removing_element(element, update)
        self._elements.remove(element)

    def copy(self) -> "Element":
        new = copy.copy(self)
        new.rect = self.rect.copy()
        new._elements = self.elements.copy()
        return new

    def index(self, element: Optional[Element]) -> int:
        """
        Returns the index of the element.
        """
        return self._elements.index(element)

    @property
    def _elements_to_render(self) -> Iterable[Element]:
        return self._elements

    @property
    def elements(self) -> list[Optional[Element]]:
        """
        Returns the child elements of the Container as a list. Read-only.
        """
        return self._elements.copy()
