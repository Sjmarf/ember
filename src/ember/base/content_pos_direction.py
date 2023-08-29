from abc import ABC, abstractmethod
from typing import Optional

from ember.position import PositionType, Position

from .content_pos import ContentX, ContentY, ContentPos
from .directional import (
    Horizontal,
    Vertical,
)


class PerpendicularContentPos(ABC):

    @property
    @abstractmethod
    def perpendicular_content_pos(self) -> Optional[Position]:
        ...

    @perpendicular_content_pos.setter
    @abstractmethod
    def perpendicular_content_pos(self, value: Optional[PositionType]) -> None:
        ...


class PerpendicularContentX(PerpendicularContentPos, ContentX):
    @property
    def perpendicular_content_pos(self) -> Optional[Position]:
        return self.content_x

    @perpendicular_content_pos.setter
    def perpendicular_content_pos(self, value: Optional[PositionType]) -> None:
        self.content_x = value


class PerpendicularContentY(PerpendicularContentPos, ContentY):
    @property
    def perpendicular_content_pos(self) -> Optional[Position]:
        return self.content_y

    @perpendicular_content_pos.setter
    def perpendicular_content_pos(self, value: Optional[PositionType]) -> None:
        self.content_y = value


class ParallelContentPos(ABC):

    @property
    @abstractmethod
    def parallel_content_pos(self) -> Optional[Position]:
        ...

    @parallel_content_pos.setter
    @abstractmethod
    def parallel_content_pos(self, value: Optional[PositionType]) -> None:
        ...


class ParallelContentX(ParallelContentPos, ContentX):
    @property
    def parallel_content_pos(self) -> Optional[Position]:
        return self.content_x

    @parallel_content_pos.setter
    def parallel_content_pos(self, value: Optional[PositionType]) -> None:
        self.content_x = value

class ParallelContentY(ParallelContentPos, ContentY):
    @property
    def parallel_content_pos(self) -> Optional[Position]:
        return self.content_y

    @parallel_content_pos.setter
    def parallel_content_pos(self, value: Optional[PositionType]) -> None:
        self.content_y = value


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
