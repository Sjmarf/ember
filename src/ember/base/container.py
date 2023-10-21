from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import (
    Optional,
    TYPE_CHECKING,
    Generator,
    Type,
    Sequence,
    Union,
    TypeVar
)

from ember.base.element import Element
from ember.base.context_manager import ContextManager

from ember import log
from ember.common import ElementType
from ember.trait.trait import Trait
from ember.trait.cascade_repository import CascadeRepository
from ember.trait.cascading_trait_value import CascadingTraitValue
from ..ui.text import Text

if TYPE_CHECKING:
    pass


T = TypeVar("T")
    
class Container(ContextManager, Element, ABC):
    """
    Base class for Containers. Should not be instantiated directly.
    """

    text_class: Type["Text"] = Text
    
    def __init__(
        self,
        *args,
        cascading: Union[CascadingTraitValue, Sequence[CascadingTraitValue]] = (), 
        **kwargs
        ) -> None:
        self.cascading: CascadeRepository = CascadeRepository(self, (cascading,) if isinstance(cascading, CascadingTraitValue) else cascading)
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
            raise ValueError(f"Tried to add a container ({self}) as a child element of itself, which isn't allowed.")
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
