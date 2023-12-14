from typing import (
    Union,
    Sequence,
    Optional,
    TYPE_CHECKING,
)

import inspect

from abc import ABC, ABCMeta, abstractmethod

from ember.axis import Axis, VERTICAL, HORIZONTAL
from ember.trait.trait_dependency import TraitDependency

if TYPE_CHECKING:
    from ember.trait.trait import Trait
    from ember.ui.can_pivot import CanPivot


def load_size(
    value: Union["Size", float, "Trait", None]
) -> Union["Size", "Trait", None]:
    from .absolute_size import AbsoluteSize

    if isinstance(value, (float, int)):
        return AbsoluteSize(value)
    return value


class SizeMeta(ABCMeta):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        
    def calculate_class_intents(cls: "Size") -> None:
        
        if (func := getattr(cls, "_get", None)) is not None:
            cls.min_value_intent = False
            cls.max_value_intent = False
            cls.other_value_intent = False
            cls.resizable_value_intent = False
            
            for param in inspect.signature(func).parameters:
                if param.kind in {param.VAR_POSITIONAL, param.VAR_KEYWORD}:
                    cls.min_value_intent = True
                    cls.max_value_intent = True
                    cls.other_value_intent = True
                    cls.resizable_value_intent = True
                    return
                
                if param.name == "min_value":
                    cls.min_value_intent = True
                elif param.name == "max_value":
                    cls.max_value_intent = True
                elif param.name == "other_value":
                    cls.other_value_intent = True
                elif param.name == "resizable_value":
                    cls.resizable_value_intent = True

        else:
            raise AttributeError("Class does not implement _get method.")
    
    

class Size(TraitDependency, ABC):
    
    min_value_intent: bool = False
    max_value_intent: bool = False
    other_value_intent: bool = False
    resizable_value_intent: bool = False

    def get(
        self,
        min_value: float = 0,
        max_value: Optional[float] = None,
        other_value: float = 0,
        axis: Axis = VERTICAL,
    ) -> float:
        ...

    @abstractmethod
    def copy(self) -> "Size":
        ...


class ContainerSize(Size, ABC):
    @abstractmethod
    def update_pair_value(self, value: float) -> bool:
        ...


SizeType = Union[Size, int]
SequenceSizeType = Union[SizeType, Sequence[SizeType]]
OptionalSequenceSizeType = Union[Optional[SizeType], Sequence[Optional[SizeType]]]


class PivotableSize(Size):

    @property
    def relies_on_min_value(self):
        return self.horizontal_size.relies_on_min_value or self.vertical_size.relies_on_min_value

    @property
    def relies_on_max_value(self):
        return self.horizontal_size.relies_on_max_value or self.vertical_size.relies_on_max_value

    @property
    def relies_on_other_value(self):
        return self.horizontal_size.relies_on_other_value or self.vertical_size.relies_on_other_value

    def __init__(
        self,
        horizontal_size: SizeType,
        vertical_size: SizeType,
        watching: Optional["CanPivot"] = None,
    ) -> None:
        self.horizontal_size: Size = load_size(horizontal_size)
        self.vertical_size: Size = load_size(vertical_size)
        self.watching: Optional["CanPivot"] = watching
        super().__init__()

    def __repr__(self):
        return f"<PivotableSize({self.horizontal_size} | {self.vertical_size})>"

    def get(
        self,
        min_value: float = 0,
        max_value: Optional[float] = None,
        other_value: float = 0,
        axis: Axis = VERTICAL,
    ) -> float:
        if self.watching is not None:
            axis = self.watching.axis
        if axis == HORIZONTAL:
            return self.horizontal_size.get(min_value, max_value, other_value, axis)
        return self.vertical_size.get(min_value, max_value, other_value, axis)

    def copy(self) -> "Size":
        return PivotableSize(self.horizontal_size, self.vertical_size, self.watching)

    def __invert__(self) -> "PivotableSize":
        return PivotableSize(self.vertical_size, self.horizontal_size, self.watching)
