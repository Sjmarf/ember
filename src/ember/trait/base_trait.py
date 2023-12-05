from abc import ABC, abstractmethod
from typing import Type, Generic, TypeVar, Optional, TYPE_CHECKING
from contextlib import contextmanager

from . import trait_layer
from .trait_layer import TraitLayer
from .cascading_trait_value import CascadingTraitValue

if TYPE_CHECKING:
    from ember.ui.element import Element

T = TypeVar("T")
class BaseTrait(Generic[T], ABC):

    @abstractmethod
    def __get__(self, instance: "Element", owner: Type["Element"]) -> T:
        ...

    @abstractmethod
    def __set__(self, instance: "Element", value: T) -> None:
        ...

    @classmethod
    @contextmanager
    def inspecting(cls, layer: TraitLayer) -> None:
        """
        Use as a context manager to set the currently inspected TraitLayer.
        """
        prev_value = trait_layer.inspected
        trait_layer.inspected = layer
        yield
        trait_layer.inspected = prev_value
