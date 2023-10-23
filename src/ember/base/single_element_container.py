import pygame
from abc import ABC
from typing import Optional, Sequence, Union, TypeVar, Generic

from ember import log

from ember.size import SizeType, SequenceSizeType, OptionalSequenceSizeType
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)
from ember.common import ElementType
from ember.size import FILL, FillSize, FitSize
from ember.trait.trait import Trait
from ember.trait.cascading_trait_value import CascadingTraitValue
from .container import Container


from .element import Element

T = TypeVar("T", bound=ElementType, covariant=True)


class SingleElementContainer(
    Generic[T], Container, ABC
):
    def __init__(
        self,
        element: Optional[T] = None,
        **kwargs
    ):
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

    def _build(self) -> None:
        super()._build()
        if self._element is not None:
            if isinstance(self._w.element_value, FitSize):
                if isinstance(self._element._w.element_value, FillSize):
                    log.size.info(
                        "Element has FILL width and we have FIT width, updating own width...",
                        self,
                    )
                    self.set_w(FILL, update=False)

            if isinstance(self._h.element_value, FitSize):
                if isinstance(self._element._h.element_value, FillSize):
                    log.size.info(
                        "Element has FILL width and we have FIT width, updating own width...",
                        self,
                    )
                    self.set_h(FILL, update=False)

            self._prepare_element(self._element)
            self._element.build()
            
    def _prepare_element(self, element: Element) -> None:
        for value in self.cascading:
            self.start_cascade(value)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        if self._element is not None and self._element.visible:
            self._element.render(surface, offset, alpha=alpha)

    def _update(self) -> None:
        super()._update()
        if self._element is not None and self._element.visible:
            self._element.update()

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        if self._element is not None:
            element_w = self._element.get_abs_w(w, self._element.axis)
            element_h = self._element.get_abs_h(h, self._element.axis)

            element_x = x + self._element.x.get(w, element_w, self._element.axis)
            element_y = y + self._element.y.get(h, element_h, self._element.axis)

            self._element.visible = self.visible

            self._element.update_rect(
                surface, element_x, element_y, element_w, element_h
            )

    def _update_min_size(self) -> None:
        if self._element is not None:
            self._min_size.w = self._element.get_abs_w()
            self._min_size.h = self._element.get_abs_h()
        else:
            self._min_size.w, self._min_size.h = 20, 20

    def update_ancestry(self, ancestry: list["Element"]) -> None:
        super().update_ancestry(ancestry)
        if self._element is not None:
            with log.ancestry.indent():
                self._element.update_ancestry(self.ancestry + [self])
                
    def update_cascading_value(self, value: CascadingTraitValue, depth: int) -> None:
        if value.ref in self.cascading:
            return
        super().update_cascading_value(value, depth)
        depth -= 1
        if depth != 0:
            with log.cascade.indent():
                self._element.update_cascading_value(value, depth)

    def start_cascade(self, value: CascadingTraitValue) -> None:
        with log.cascade.indent(f"Starting descent for {value}", self):
            with Trait.inspecting(Trait.Layer.PARENT):
                value.prepare_for_descent(self)
                self._element.update_cascading_value(value, value.depth)
        log.cascade.line_break()

    def _attribute_element(self, element: T) -> None:
        self.set_element(element, _update=False)

    @property
    def element(self) -> Optional[T]:
        return self._element

    @element.setter
    def element(self, element: Optional[T]) -> None:
        self.set_element(element)

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
                self.removing_element(self._element)
                with self.adding_element(element, _update) as element:
                    self._element = element
