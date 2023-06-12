import pygame
import abc
import inspect
import copy
from typing import Optional, Sequence, Union, Literal

from ember import common as _c
from ...common import INHERIT, InheritType, FocusType
from ember import log
from ember.ui.base.element import Element
from ember.ui.view import ViewLayer
from ember.size import SizeType, SequenceSizeType, SizeMode
from ember.position import PositionType, SequencePositionType
from ember.transition.transition import Transition
from ...size import FIT, FILL


from ember.state.background_state import BackgroundState
from ember.material.material import Material

from .container import Container


class MultiElementContainer(Container):
    def __init__(
        self,
        material: Union[BackgroundState, Material, None],
        rect: Union[pygame.rect.RectType, Sequence, None],
        pos: Optional[SequencePositionType],
        x: Optional[PositionType],
        y: Optional[PositionType],
        size: Optional[SequenceSizeType],
        width: Optional[SizeType],
        height: Optional[SizeType],
        focus_on_entry: Union[InheritType, FocusType]
    ):
        """
        Base class for Containers that hold more than one element. Should not be instantiated directly.
        """
        
        self.focus_on_entry: FocusType = self._style.focus_on_entry if focus_on_entry is INHERIT else focus_on_entry
        """
        Whether the closest or first element of the container should be focused when the container is entered.
        """        
        
        default_size = self._style.size
        if self._style.sizes is not None:
            for cls in inspect.getmro(type(self)):
                if cls in self._style.sizes:
                    default_size = self._style.sizes[cls]
                    break

        if not isinstance(default_size, Sequence):
            default_size = default_size, default_size

        if default_size[0] == FIT:
            default_size = (
                FILL if any(i._w.mode == SizeMode.FILL for i in self._elements) else FIT,
                default_size[1]
            )

        if default_size[1] == FIT:
            default_size = (
                default_size[0],
                FILL if any(i._h.mode == SizeMode.FILL for i in self._elements) else FIT,
            )

        super().__init__(material, rect, pos, x, y, size, width, height, default_size=default_size)

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
            raise ValueError(f"{type(self).__name__} element must be of type Element, not {type(element).__name__}.")
        element._set_parent(self)
        log.layer.line_break()
        log.layer.info(self, "Element added to container - starting chain...")
        with log.layer.indent:
            element._set_layer_chain(self.layer)
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
        *elements: Union[Element, Sequence[Element]],
        transition: Optional[Transition] = None,
        _update: bool = True,
    ) -> None:
        """
        Replace the elements in the stack with new elements.
        """

        if elements and isinstance(elements[0], Sequence):
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

    def append(self, element: Element, transition: Optional[Transition] = None) -> None:
        """
        Append an element to the end of the stack.
        """
        old_container = self.copy() if transition else None
        self._elements.append(self._load_element(element))
        self._update_elements(transition=transition, old_container=old_container)

    def insert(
        self, index: int, element: Element, transition: Optional[Transition] = None
    ) -> None:
        """
        Insert an element before at an index.
        """
        old_container = self.copy() if transition else None
        self._elements.insert(index, self._load_element(element))
        self._update_elements(transition=transition, old_container=old_container)

    def pop(self, index: int = -1, transition: Optional[Transition] = None) -> Element:
        """
        Remove and return an element at an index (default last).
        """
        old_container = self.copy() if transition else None
        element = self._elements.pop(index)

        if self.layer is not None:
            if self.layer.element_focused is element:
                self.layer._focus_element(None)
        self._update_elements(transition=transition, old_container=old_container)
        return element

    def remove(self, element: Element, transition: Optional[Transition] = None) -> None:
        """
        Remove an element from the stack.
        """
        old_container = self.copy() if transition else None
        self._elements.remove(element)

        if self.layer is not None:
            if self.layer.element_focused is element:
                self.layer._focus_element(None)
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

    elements = property(
        fget=lambda self: self._elements.copy(),
        doc="Returns the child elements of the Container as a list. Read-only.",
    )
