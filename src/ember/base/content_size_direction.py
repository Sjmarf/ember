from abc import ABC, abstractmethod
from typing import Optional

from ember.size import Size, SizeType

from .content_size import ContentW, ContentH, ContentSize
from .directional import (
    Directional,
    Horizontal,
    Vertical,
)


class PerpendicularContentSize(ABC):
    @property
    @abstractmethod
    def perpendicular_content_size(self) -> Optional[Size]:
        ...

    @perpendicular_content_size.setter
    @abstractmethod
    def perpendicular_content_size(self, value: Optional[SizeType]) -> None:
        ...


class PerpendicularContentW(PerpendicularContentSize, ContentW):
    @property
    def perpendicular_content_size(self) -> Optional[Size]:
        return self.content_w

    @perpendicular_content_size.setter
    def perpendicular_content_size(self, value: Optional[SizeType]) -> None:
        self.content_w = value


class PerpendicularContentH(PerpendicularContentSize, ContentH):
    @property
    def perpendicular_content_size(self) -> Optional[Size]:
        return self.content_h

    @perpendicular_content_size.setter
    def perpendicular_content_size(self, value: Optional[SizeType]) -> None:
        self.content_h = value


class ParallelContentSize(ABC):
    @property
    @abstractmethod
    def parallel_content_size(self) -> Optional[Size]:
        ...

    @parallel_content_size.setter
    @abstractmethod
    def parallel_content_size(self, value: Optional[SizeType]) -> None:
        ...


class ParallelContentW(ParallelContentSize, ContentW):
    @property
    def parallel_content_size(self) -> Optional[Size]:
        return self.content_w

    @parallel_content_size.setter
    def parallel_content_size(self, value: Optional[SizeType]) -> None:
        self.content_w = value


class ParallelContentH(ParallelContentSize, ContentH):
    @property
    def parallel_content_size(self) -> Optional[Size]:
        return self.content_h

    @parallel_content_size.setter
    def parallel_content_size(self, value: Optional[SizeType]) -> None:
        self.content_h = value

class DirectionalContentSize(
    ParallelContentSize,
    PerpendicularContentSize,
    ContentSize,
    Directional,
    ABC,
):
    pass


class HorizontalContentSize(
    ParallelContentW,
    PerpendicularContentH,
    DirectionalContentSize,
    Horizontal,
):
    pass


class VerticalContentSize(
    ParallelContentH,
    PerpendicularContentW,
    DirectionalContentSize,
    Vertical,
):
    pass
