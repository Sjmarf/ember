from abc import abstractmethod
from typing import Union

from ember.size import SizeType
from ember.position import PositionType
from ember.trait.trait import Trait
from ember.base.element import Element


class Directional(Element):
    @abstractmethod
    def set_parallel_size(
        self, value: Union[SizeType, Trait, None], update=True
    ) -> None:
        ...

    @abstractmethod
    def set_perpendicular_size(
        self, value: Union[SizeType, Trait, None], update=True
    ) -> None:
        ...

    @abstractmethod
    def set_parallel_pos(
        self, value: Union[PositionType, Trait, None], update=True
    ) -> None:
        ...

    @abstractmethod
    def set_perpendicular_pos(
        self, value: Union[PositionType, Trait, None], update=True
    ) -> None:
        ...


class Horizontal(Directional):
    def set_parallel_size(
        self, value: Union[SizeType, Trait, None], update=True
    ) -> None:
        self.set_w(value, update=update)

    def set_perpendicular_size(
        self, value: Union[SizeType, Trait, None], update=True
    ) -> None:
        self.set_h(value, update=update)

    def set_parallel_pos(
        self, value: Union[PositionType, Trait, None], update=True
    ) -> None:
        self.set_x(value, update=update)

    def set_perpendicular_pos(
        self, value: Union[PositionType, Trait, None], update=True
    ) -> None:
        self.set_y(value, update=update)


class Vertical(Directional):
    def set_parallel_size(
        self, value: Union[SizeType, Trait, None], update=True
    ) -> None:
        self.set_h(value, update=update)

    def set_perpendicular_size(
        self, value: Union[SizeType, Trait, None], update=True
    ) -> None:
        self.set_w(value, update=update)

    def set_parallel_pos(
        self, value: Union[PositionType, Trait, None], update=True
    ) -> None:
        self.set_y(value, update=update)

    def set_perpendicular_pos(
        self, value: Union[PositionType, Trait, None], update=True
    ) -> None:
        self.set_x(value, update=update)
