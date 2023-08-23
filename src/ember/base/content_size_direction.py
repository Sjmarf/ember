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
    @abstractmethod
    def set_perpendicular_content_size(
        self, value: Optional[SizeType], update=True
    ) -> None:
        ...

    @property
    @abstractmethod
    def perpendicular_content_size(self) -> Optional[Size]:
        ...

    @perpendicular_content_size.setter
    def perpendicular_content_size(self, value: Optional[SizeType]):
        self.set_perpendicular_content_size(value)


class PerpendicularContentW(PerpendicularContentSize, ContentW):
    def set_perpendicular_content_size(
        self, value: Optional[SizeType], update=True
    ) -> None:
        self.set_content_w(value, update=update)

    @property
    def perpendicular_content_size(self) -> Optional[Size]:
        return self._content_w.value


class PerpendicularContentH(PerpendicularContentSize, ContentH):
    def set_perpendicular_content_size(
        self, value: Optional[SizeType], update=True
    ) -> None:
        self.set_content_h(value, update=update)

    @property
    def perpendicular_content_size(self) -> Optional[Size]:
        return self._content_h.value


class ParallelContentSize(ABC):
    @abstractmethod
    def set_parallel_content_size(self, value: Optional[SizeType], update=True) -> None:
        ...

    @property
    @abstractmethod
    def parallel_content_size(self) -> Optional[Size]:
        ...

    @parallel_content_size.setter
    def parallel_content_size(self, value: Optional[SizeType]):
        self.set_parallel_content_size(value)


class ParallelContentW(ParallelContentSize, ContentW):
    def set_parallel_content_size(self, value: Optional[SizeType], update=True) -> None:
        self.set_content_w(value, update=update)

    @property
    def parallel_content_size(self) -> Optional[Size]:
        return self._content_w.value


class ParallelContentH(ParallelContentSize, ContentH):
    def set_parallel_content_size(self, value: Optional[SizeType], update=True) -> None:
        self.set_content_h(value, update=update)

    @property
    def parallel_content_size(self) -> Optional[Size]:
        return self._content_h.value


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
