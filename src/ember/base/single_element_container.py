import pygame
from abc import ABC
from typing import Optional, Sequence, Union, TypeVar, Generic

from ember import log

from .content_pos import ContentPos
from ember.base.content_size import ContentSize
from ember.size import SizeType, SequenceSizeType, OptionalSequenceSizeType
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)
from ember.common import ElementType
from ember.size import FILL, FillSize, FitSize
from ember.trait.trait import Trait
from .container import Container


from .element import Element

T = TypeVar("T", bound=ElementType, covariant=True)


class SingleElementContainer(
    Generic[T], ContentPos, ContentSize, Container, ABC
):
    def __init__(
        self,
        element: Optional[T] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        **kwargs
    ):
        """
        Base class for Containers that hold one or zero elements. Should not be instantiated directly.
        """

        self._element: Optional[T] = None

        super().__init__(
            # Container
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            # ContentSize
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
            **kwargs
        )

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

    def _prepare_element(self, element: Optional[Element]):
        """
        Prepares an element for use as a child of the container,
        """
        if element is None:
            return

        with Trait.inspecting(Trait.Layer.PARENT):
            self._element.x = self._content_x
            self._element.y = self._content_y
            self._element.w = self._content_w
            self._element.h = self._content_h

    def _build(self) -> None:
        super()._build()
        self.layer.can_focus_update_queue.append(self)
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

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        if self._element and self._element.visible:
            self._element.render(surface, offset, alpha=alpha)

    def _update(self) -> None:
        if self._element and self._element.visible:
            self._element.update()

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        if self._element is not None:
            element_w = self._element.get_abs_w(w)
            element_h = self._element.get_abs_h(h)

            element_x = x + self._element.x.get(w, element_w)
            element_y = y + self._element.y.get(h, element_h)

            self._element.visible = self.visible

            self._element.update_rect(
                surface, element_x, element_y, element_w, element_h
            )

    def _update_min_size(self) -> None:
        if self._element:
            self._min_w = self._element.get_abs_w()
            self._min_h = self._element.get_abs_h()
        else:
            self._min_w, self._min_h = 20, 20

    def update_ancestry(self, ancestry: list["Element"]) -> None:
        super().update_ancestry(ancestry)
        if self._element is not None:
            with log.ancestry.indent():
                self._element.update_ancestry(self.ancestry + [self])

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
        if element is not self._element:
            self.removing_element(self._element)
            with self.adding_element(element, _update):
                self._element = element
