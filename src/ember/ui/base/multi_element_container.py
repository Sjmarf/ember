import pygame
import abc
import inspect
import copy
from typing import Optional, Sequence, Union, Literal, Generator, TYPE_CHECKING

from ember import common as _c
from ...common import INHERIT, InheritType, FocusType
from ember import log
from ember.ui.base.element import Element
from ember.ui.view import ViewLayer

from ...size import FILL, OptionalSequenceSizeType, SizeType, FillSize, FitSize
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)
from ember.transition.transition import Transition

from .has_content_size import ContentHMixin, ContentWMixin

from ember.state.background_state import BackgroundState
from ember.material.material import Material

from .container import Container

if TYPE_CHECKING:
    from ...style.style import Style
    from ...style.container_style import ContainerStyle


class MultiElementContainer(Container):
    def __init__(
        self,
        elements: tuple[
            Union[Element, Sequence[Element], Generator[Element, None, None]]
        ],
        material: Union[BackgroundState, Material, None],
        focus_on_entry: Union[InheritType, FocusType],
        rect: Union[pygame.rect.RectType, Sequence, None],
        pos: Optional[SequencePositionType],
        x: Optional[PositionType],
        y: Optional[PositionType],
        size: OptionalSequenceSizeType,
        w: Optional[SizeType],
        h: Optional[SizeType],
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        style: Optional["Style"] = None,
    ):
        """
        Base class for Containers that hold more than one element. Should not be instantiated directly.
        """

        super().__init__(
            material,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            style=style,
        )

        self.set_elements(*elements, _update=False)

        self.focus_on_entry: FocusType = (
            self._style.focus_on_entry if focus_on_entry is INHERIT else focus_on_entry
        )
        """
        Whether the closest or first element of the container should be focused when the container is entered.
        """

    def __getitem__(self, item: int) -> Element:
        if isinstance(item, int):
            return self._elements[item]
        else:
            return NotImplemented

    def __setitem__(self, key: int, value: Element):
        if not isinstance(key, int) or not isinstance(value, Element):
            return NotImplemented

        self._elements[key] = value
        value._set_parent(self)
        self._update_rect_chain_up()

    def __len__(self) -> int:
        return len(self._elements)

    def __contains__(self, item: Element) -> bool:
        return item in self._elements

    def _build_chain(self) -> None:
        if self._has_built:
            return
        self._has_built = True
        for element in self._elements:
            element._build_chain()

            if isinstance(self._active_w, FitSize):
                if isinstance(self, ContentWMixin):
                    element.set_active_w(self.content_w)
                if isinstance(element._active_w, FillSize):
                    log.size.info(self, "Element has FILL width and we have FIT width, updating own width...")
                    self.set_w(FILL, _update=False)

            if isinstance(self._active_h, FitSize):
                if isinstance(self, ContentHMixin):
                    element.set_active_h(self.content_h)
                if isinstance(element._active_h, FillSize):
                    log.size.info(self, "Element has FILL width and we have FIT width, updating own width...")
                    self.set_h(FILL, _update=False)

        log.size.info(self, "Element built, starting chain up without proprogation.")
        with log.size.indent:
            self._update_rect_chain_up(_update=False)

    @abc.abstractmethod
    def _render_elements(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        pass

    def _set_layer_chain(self, layer: ViewLayer) -> None:
        log.layer.info(self, f"Set layer to {layer}")
        self.layer = layer
        [i._set_layer_chain(layer) for i in self._elements]

    def _load_element(self, element: Element) -> Element:
        if not isinstance(element, Element):
            raise ValueError(
                f"{type(self).__name__} element must be of type Element, not {type(element).__name__}."
            )
        
        element._set_parent(self)
        log.layer.line_break()
        log.layer.info(self, "Element added to container - starting chain...")
        with log.layer.indent:
            element._set_layer_chain(self.layer)
        element._build_chain()
        return element

    def _update_elements(
        self,
        transition: Optional[Transition] = None,
        old_container: Optional[Container] = None,
    ) -> None:
        if transition:
            self._transition = transition._new_element_controller()
            self._transition.old = old_container
            self._transition.new = self

        log.size.info(self, "Elements set, starting chain up...")
        with log.size.indent:
            self._update_rect_chain_up()

    def set_elements(
        self,
        *elements: Union[Element, Sequence[Element], Generator[Element, None, None]],
        transition: Optional[Transition] = None,
        _update: bool = True,
    ) -> None:
        """
        Replace the elements in the stack with new elements.
        """
        if elements:
            if isinstance(elements[0], Generator):
                elements = elements[0]
            elif isinstance(elements[0], Sequence):
                elements = list(elements[0])

        old_container = self.copy() if transition else None
        if self.layer is not None:
            if (
                self.layer.element_focused in self._elements
                and self.layer.element_focused not in elements
            ):
                self.layer._focus_element(None)

        self._elements.clear()
        for i in elements:
            self._elements.append(self._load_element(i))
        if _update:
            self._update_elements(transition=transition, old_container=old_container)

    def _attribute_element(self, element: "Element") -> None:
        self.append(element, _update=False)

    def append(self, element: Element, transition: Optional[Transition] = None, _update: bool = True) -> None:
        """
        Append an element to the end of the stack.
        """
        old_container = self.copy() if transition else None
        self._elements.append(self._load_element(element))
        if _update:
            self._update_elements(transition=transition, old_container=old_container)

    def insert(
        self, index: int, element: Element, transition: Optional[Transition] = None, _update: bool = True
    ) -> None:
        """
        Insert an element before at an index.
        """
        old_container = self.copy() if transition else None
        self._elements.insert(index, self._load_element(element))
        if _update:
            self._update_elements(transition=transition, old_container=old_container)

    def pop(self, index: int = -1, transition: Optional[Transition] = None, _update: bool = True) -> Element:
        """
        Remove and return an element at an index (default last).
        """
        old_container = self.copy() if transition else None
        element = self._elements.pop(index)

        if self.layer is not None:
            if self.layer.element_focused is element:
                self.layer._focus_element(None)
        if _update:
            self._update_elements(transition=transition, old_container=old_container)
        return element

    def remove(self, element: Element, transition: Optional[Transition] = None, _update: bool = True) -> None:
        """
        Remove an element from the stack.
        """
        old_container = self.copy() if transition else None
        self._elements.remove(element)

        if self.layer is not None:
            if self.layer.element_focused is element:
                self.layer._focus_element(None)
        if _update:
            self._update_elements(transition=transition, old_container=old_container)

    def copy(self) -> "Element":
        new = copy.copy(self)
        new.rect = self.rect.copy()
        new._elements = self.elements.copy()
        return new

    def index(self, element: Element) -> int:
        """
        Returns the index of the element.
        """
        return self._elements.index(element)

    @property
    def elements(self) -> list[Element]:
        """
        "Returns the child elements of the Container as a list. Read-only.
        """
        return self._elements.copy()
