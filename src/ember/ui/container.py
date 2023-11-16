import pygame
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import (
    Optional,
    TYPE_CHECKING,
    Generator,
    Type,
    Sequence,
    Union,
    TypeVar,
    Iterable,
)

from ember.ui.element import Element
from ember.ui.context_manager import ContextManager

from ember import log
from ember.common import ElementType
from ember.trait.trait import Trait
from ember.trait.cascade_repository import CascadeRepository
from ember.trait.cascading_trait_value import CascadingTraitValue
from ember.ui.text import Text
from ember.size import FillSize

from .element_meta import ElementMeta

if TYPE_CHECKING:
    pass


T = TypeVar("T")


class ContainerMeta(ElementMeta):
    _context_stack: list["Container"] = []

    def __enter__(cls) -> "Container":
        new = cls()
        new.__enter__()
        ContainerMeta._context_stack.append(new)
        return new

    def __exit__(cls, *args):
        cont = ContainerMeta._context_stack.pop()
        cont.__exit__(*args)


class Container(Element, ABC, metaclass=ContainerMeta):
    """
    Base class for Containers. Should not be instantiated directly.
    """

    text_class: Type["Text"] = Text

    def __init__(
        self,
        *args,
        cascading: Union[CascadingTraitValue, Sequence[CascadingTraitValue]] = (),
        **kwargs,
    ) -> None:
        self.cascading: CascadeRepository = CascadeRepository(
            self,
            (cascading,) if isinstance(cascading, CascadingTraitValue) else cascading,
        )
        super().__init__(*args, **kwargs)

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

    def start_cascade(self, value: CascadingTraitValue) -> None:
        with log.cascade.indent(f"Starting descent for {value}", self):
            with Trait.inspecting(Trait.Layer.PARENT):
                value.prepare_for_descent(self)
                for element in self._elements_to_render:
                    if element is not None:
                        element.update_cascading_value(value, value.depth)
        log.cascade.line_break()

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

            element_w = element.get_w(w)
            element_h = element.get_h(h)
            element_x = x + element.get_x(w, element_w)
            element_y = y + element.get_y(h, element_h)

            element.visible = self.visible
            element.update_rect(surface, element_x, element_y, element_w, element_h)

    def _update_min_size(self) -> None:
        self._min_size.w = 0
        for i in self._elements_to_render:
            if i is None or isinstance(i.w, FillSize):
                continue
            if (w := i.get_w()) > self._min_size.w:
                self._min_size.w = w

        self._min_size.h = 0
        for i in self._elements_to_render:
            if i is None or isinstance(i.h, FillSize):
                continue
            if (h := i.get_h()) > self._min_size.h:
                self._min_size.h = h

    def _event(self, event: pygame.event.Event) -> bool:
        for i in self._elements_to_render:
            if i is not None and i.event(event):
                return True
        return super()._event(event)

    def update_ancestry(self, ancestry: list["Element"]) -> None:
        super().update_ancestry(ancestry)
        child_ancestry = self.ancestry + [self]
        with log.ancestry.indent():
            [
                i.update_ancestry(child_ancestry)
                for i in self._elements_to_render
                if i is not None
            ]

    def update_cascading_value(self, value: CascadingTraitValue, depth: int) -> None:
        super().update_cascading_value(value, depth)
        if value.ref in self.cascading:
            return
        depth -= 1
        if depth == 0:
            return
        with log.cascade.indent():
            for element in self._elements_to_render:
                element.update_cascading_value(value, depth)

    @property
    @abstractmethod
    def _elements_to_render(self) -> Iterable[Element]:
        ...

    def make_visible(self, element: Element) -> None:
        self.parent.make_visible(element)

    @contextmanager
    def adding_element(
        self, element: ElementType, update: bool = True
    ) -> Generator[Optional["Element"], None, None]:
        if isinstance(element, str):
            element = self.text_class(element)

        if element is not None:
            log.ancestry.line_break()
            with log.ancestry.indent(
                f"Element {element} added to Container - starting chain with {len(self.ancestry)}, parent = {self.parent}, layer = {self.layer}...",
                self,
            ):
                element.update_ancestry(self.ancestry + [self])
        if element is self:
            raise ValueError(
                f"Tried to add a container ({self}) as a child element of itself, which isn't allowed."
            )
        yield element

        if self._has_built:
            if element is not None:
                with Trait.inspecting(Trait.Layer.PARENT):
                    self._prepare_element(element)
                    element.build()
            if update:
                self.update_min_size_next_tick()
                self.update_rect_next_tick()

    def removing_element(
        self, element: Optional["Element"], update: bool = True
    ) -> None:
        if element is not None:
            element.update_ancestry([])
            if self.layer is not None:
                if self.layer.element_focused is element:
                    self.layer._focus_element(None)
        if self._has_built and update:
            self.update_min_size_next_tick()
            self.update_rect_next_tick()
