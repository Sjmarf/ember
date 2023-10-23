from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, TYPE_CHECKING, Generator, Type, Sequence, Union, TypeVar

from ember_ui.ui.element import Element
from ember_ui.ui.context_manager import ContextManager

from ember_ui import log
from ember_ui.common import ElementType
from ember_ui.trait.trait import Trait
from ember_ui.trait.cascade_repository import CascadeRepository
from ember_ui.trait.cascading_trait_value import CascadingTraitValue
from ember_ui.ui.text import Text

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
    

class Container(ContextManager, Element, ABC, metaclass=ContainerMeta):
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

    def _prepare_element(self, element: Element) -> None:
        ...

    @abstractmethod
    def start_cascade(self, value: CascadingTraitValue) -> None:
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
