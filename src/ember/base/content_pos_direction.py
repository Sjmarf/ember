from abc import ABC, abstractmethod
from typing import Optional

from ember.position import PositionType, Position

from .content_pos import ContentX, ContentY, ContentPos
from .directional import (
    Horizontal,
    Vertical,
)


class PerpendicularContentPos(ABC):
    @abstractmethod
    def set_perpendicular_content_pos(
        self, value: Optional[PositionType], update=True
    ) -> None:
        ...

    @property
    @abstractmethod
    def perpendicular_content_pos(self) -> Optional[Position]:
        ...

    @perpendicular_content_pos.setter
    def perpendicular_content_pos(self, value: Optional[PositionType]):
        self.set_perpendicular_content_pos(value)


class PerpendicularContentX(PerpendicularContentPos, ContentX):
    def set_perpendicular_content_pos(
        self, value: Optional[PositionType], update=True
    ) -> None:
        self.set_content_x(value, update=update)

    @property
    def perpendicular_content_pos(self) -> Optional[Position]:
        return self._content_x.value


class PerpendicularContentY(PerpendicularContentPos, ContentY):
    def set_perpendicular_content_pos(
        self, value: Optional[PositionType], update=True
    ) -> None:
        self.set_content_y(value, update=update)

    @property
    def perpendicular_content_pos(self) -> Optional[Position]:
        return self._content_y.value


class ParallelContentPos(ABC):
    @abstractmethod
    def set_parallel_content_pos(
        self, value: Optional[PositionType], update=True
    ) -> None:
        ...

    @property
    @abstractmethod
    def parallel_content_pos(self) -> Optional[Position]:
        ...

    @parallel_content_pos.setter
    def parallel_content_pos(self, value: Optional[PositionType]):
        self.set_parallel_content_pos(value)


class ParallelContentX(ParallelContentPos, ContentX):
    def set_parallel_content_pos(
        self, value: Optional[PositionType], update=True
    ) -> None:
        self.set_content_x(value, update=update)

    @property
    def parallel_content_pos(self) -> Optional[Position]:
        return self._content_x.value


class ParallelContentY(ParallelContentPos, ContentY):
    def set_parallel_content_pos(
        self, value: Optional[PositionType], update=True
    ) -> None:
        self.set_content_y(value, update=update)

    @property
    def parallel_content_pos(self) -> Optional[Position]:
        return self._content_y.value


class DirectionalContentPos(
    ParallelContentPos, PerpendicularContentPos, ContentPos, ABC
):
    pass


class HorizontalContentPos(
    ParallelContentX,
    PerpendicularContentY,
    DirectionalContentPos,
    Horizontal,
):
    pass


class VerticalContentPos(
    ParallelContentY,
    PerpendicularContentX,
    DirectionalContentPos,
    Vertical,
):
    pass
