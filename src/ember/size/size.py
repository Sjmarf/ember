from typing import Union, Sequence, Optional
from abc import ABC, abstractmethod


class Size(ABC):
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

    @abstractmethod
    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0) -> float:
        pass


SizeType = Union[Size, int]
SequenceSizeType = Union[SizeType, Sequence[SizeType]]
OptionalSequenceSizeType = Union[Optional[SizeType], Sequence[Optional[SizeType]]]
