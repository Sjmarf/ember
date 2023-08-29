from abc import ABC
from contextlib import contextmanager
from typing import (
    Optional,
    TYPE_CHECKING,
    Generator,
    Type
)

from ember.base.element import Element
from ember.base.context_manager import ContextManager

from ember import log
from ember.common import ElementType
from ember.trait.trait import Trait
from ..ui.text import Text

from .content_pos import ContentX, ContentY
from ember.base.content_size import ContentW, ContentH

if TYPE_CHECKING:
    pass


class Container(ContextManager, Element, ABC):
    """
    Base class for Containers. Should not be instantiated directly.
    """

    text_class: Type["Text"] = Text

    def _prepare_element(self, element: Element) -> None:
        if isinstance(self, ContentX):
            element.x = self._content_x
        if isinstance(self, ContentY):
            element.y = self._content_y
        if isinstance(self, ContentW):
            element.w = self._content_w
        if isinstance(self, ContentH):
            element.h = self._content_h

    def update_can_focus(self) -> None:
        """
        Update the can_focus attribute of the container.
        """

    def make_visible(self, element: Element) -> None:
        self.parent.make_visible(element)

    @contextmanager
    def adding_element(
        self, element: ElementType, update: bool = False
    ) -> Generator[Optional["Element"], None, None]:

        if isinstance(element, str):
            element = self.text_class(element)

        if element is not None:
            log.ancestry.line_break()
            with log.ancestry.indent(
                f"Element {element} added to Container - starting chain with layer {self.layer}...",
                self,
            ):
                element.update_ancestry(self.ancestry + [self])
        yield element

        if self._has_built:
            if element is not None:
                with Trait.inspecting(Trait.Layer.PARENT):
                    self._prepare_element(element)
                    element.build()
            if update:
                self.update_min_size_next_tick()
                if self not in self.layer.can_focus_update_queue:
                    self.layer.can_focus_update_queue.append(self)

    def removing_element(
        self, element: Optional["Element"], update: bool = False
    ) -> None:
        if element is not None:
            element.update_ancestry([])
            if self.layer is not None:
                if self.layer.element_focused is element:
                    self.layer._focus_element(None)
        if update:
            self.update_min_size_next_tick()
            if self not in self.layer.can_focus_update_queue:
                self.layer.can_focus_update_queue.append(self)
