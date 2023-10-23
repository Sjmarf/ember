from typing import (
    Union,
    Sequence,
    Optional,
    TYPE_CHECKING,
    Callable,
    ParamSpec,
    Self,
    Generator,
)
from contextlib import contextmanager
from abc import ABC, abstractmethod
from weakref import WeakSet

from ember_ui import log
from ember_ui.axis import Axis, VERTICAL, HORIZONTAL
from ember_ui.trait.trait_dependency import TraitDependency

if TYPE_CHECKING:
    from ember_ui.trait.trait_context import TraitContext
    from ember_ui.trait.trait import Trait


def load_size(
    value: Union["Size", float, "Trait", None]
) -> Union["Size", "Trait", None]:
    from .absolute_size import AbsoluteSize

    if isinstance(value, (float, int)):
        return AbsoluteSize(value)
    return value


class Size(TraitDependency, ABC):
    relies_on_min_value: bool = False
    """
    Should be True when the Size takes the min_value into account in any way. This tells the Element to keep
    the min_value exact - if this value is False, the Element will avoid updating the min_value if possible.
    """

    relies_on_max_value: bool = False
    """
    Should be True when the Size takes the max_value into account in any way. This tells the Element to keep
    the max_value exact - if this value is False, the Element will avoid updating the max_value if possible.
    """

    relies_on_other_value: bool = False
    """
    Should be True when the Size takes the other_value into account in any way. This tells the Element to keep
    the other_value exact - if this value is False, the Element will avoid updating the other_value if possible.
    """

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
        watching: Optional["Element"] = None,
    ) -> None:
        self.horizontal_size: Size = load_size(horizontal_size)
        self.vertical_size: Size = load_size(vertical_size)
        self.watching: Optional["Element"] = watching
        super().__init__()

    def get(
        self,
        min_value: float = 0,
        max_value: Optional[float] = None,
        other_value: float = 0,
        axis: Axis = VERTICAL,
    ) -> float:
        if self.watching is not None:
            axis = self.watching._axis
        if axis == HORIZONTAL:
            return self.horizontal_size.get(min_value, max_value, other_value, axis)
        return self.vertical_size.get(min_value, max_value, other_value, axis)

    def copy(self) -> "Size":
        return PivotableSize(self.horizontal_size, self.vertical_size, self.watching)

    def __invert__(self) -> "PivotableSize":
        return PivotableSize(self.vertical_size, self.horizontal_size, self.watching)
