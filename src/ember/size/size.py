from typing import (
    Union,
    Sequence,
    Optional,
    TYPE_CHECKING,
    Iterable
)

from abc import ABC, abstractmethod

from ember.axis import Axis, VERTICAL, HORIZONTAL
from ember.trait.trait_dependency import TraitDependency
from ember.trait.dependency_child import DependencyChild
from .size_meta import SizeMeta

if TYPE_CHECKING:
    from ember.trait.trait import Trait
    from ember.ui.can_pivot import CanPivot


def load_size(
    value: Union["Size", float, "Trait", None]
) -> Union["Size", "Trait", None]:
    from .absolute_size import Absolute

    if isinstance(value, (float, int)):
        return Absolute(value)
    return value
    

class Size(TraitDependency, ABC, metaclass=SizeMeta):
    
    min_value_intent: bool = False
    max_value_intent: bool = False
    other_value_intent: bool = False
    resizable_value_intent: bool = False
    axis_intent: bool = False
    
    def calculate_instance_intents(self) -> None:
        if isinstance(self, Iterable):
            cls = type(self)
            if not cls.min_value_intent:
                self.min_value_intent = False
            if not cls.max_value_intent:
                self.max_value_intent = False
            if not cls.other_value_intent:
                self.other_value_intent = False
            if not cls.resizable_value_intent:
                self.resizable_value_intent = False
            if not cls.axis_intent:
                self.axis_intent = False
            
            for child in self:
                if child.min_value_intent:
                    self.min_value_intent = True
                if child.max_value_intent:
                    self.max_value_intent = True
                if child.other_value_intent:
                    self.other_value_intent = True
                if child.resizable_value_intent:
                    self.resizable_value_intent = True
                if child.axis_intent:
                    self.axis_intent = True
                    
    def child_updated(self):
        self.calculate_instance_intents()

    def get(
        self,
        min_value: float = 0,
        max_value: float = 0,
        other_value: float = 0,
        resizable_value: float = 0,
        axis: Axis = VERTICAL,
    ) -> float:
        kwargs = {}
        if self.min_value_intent:
            kwargs["min_value"] = min_value
        if self.max_value_intent:
            kwargs["max_value"] = max_value
        if self.other_value_intent:
            kwargs["other_value"] = other_value
        if self.resizable_value_intent:
            kwargs["resizable_value"] = resizable_value
        if self.axis_intent:
            kwargs["axis"] = axis
        return self._get(**kwargs)
        
    @abstractmethod
    def _get() -> float:
        pass

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
    
    horizontal_size: DependencyChild[SizeType | None, Size | None] = DependencyChild(load_value_with=load_size)
    vertical_size: DependencyChild[SizeType | None, Size | None] = DependencyChild(load_value_with=load_size)

    def __init__(
        self,
        horizontal_size: SizeType,
        vertical_size: SizeType,
        watching: Optional["CanPivot"] = None,
    ) -> None:
        self.horizontal_size: Size = horizontal_size
        self.vertical_size: Size = vertical_size
        self.watching: Optional["CanPivot"] = watching
        super().__init__()

    def __repr__(self):
        return f"<PivotableSize({self.horizontal_size} | {self.vertical_size}, watching={self.watching})>"

    def _get(self, axis: Axis, **kwargs) -> float:
        if self.watching is not None:
            axis = self.watching.axis
        if axis == HORIZONTAL:
            return self.horizontal_size.get(axis=axis, **kwargs)
        return self.vertical_size.get(axis=axis, **kwargs)

    def copy(self) -> "Size":
        return PivotableSize(self.horizontal_size, self.vertical_size, self.watching)

    def __invert__(self) -> "PivotableSize":
        return PivotableSize(self.vertical_size, self.horizontal_size, self.watching)
