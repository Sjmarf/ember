import pygame
from typing import Optional, TYPE_CHECKING

from ember import log
from ..event import VALUEMODIFIED

from ember.ui.element import Element

if TYPE_CHECKING:
    pass


class Gauge(Element):
    class ValueCause:
        class Cause:
            __slots__ = ()

        PROPERTY = Cause()

    def __init__(
        self,
        *args,
        value: Optional[float] = 0,
        min_value: float = 0,
        max_value: float = 1,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._min_value: float = min_value
        self._max_value: float = max_value

        self._progress: float = 0

        self.value = value

    def __repr__(self) -> str:
        return f"<Gauge>"

    @property
    def value(self) -> float:
        return self._min_value + self._progress * (self._max_value - self._min_value)

    @value.setter
    def value(self, value: float) -> None:
        self.progress = pygame.math.clamp(
            (value - self._min_value) / (self._max_value - self._min_value), self._min_value, self._max_value
        )

    @property
    def progress(self) -> float:
        return self._progress

    @progress.setter
    def progress(self, value: float) -> None:
        self._set_progress(value, self.ValueCause.PROPERTY)

    def _set_progress(self, value: float, cause: ValueCause.Cause) -> None:
        value = pygame.math.clamp(value, 0, 1)
        if value != self._progress:
            with log.size.indent(f"Set gauge progress to {value}..."):
                self._progress = value
                if self._has_built:
                    event = pygame.event.Event(VALUEMODIFIED, element=self)
                    self._post_event(event)

    @property
    def min_value(self) -> float:
        return self._min_value

    @min_value.setter
    def min_value(self, value: min_value) -> None:
        if self._min_value != value:
            current_value = self.value
            self._min_value = value
            self.value = current_value

    @property
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, value: min_value) -> None:
        if self._max_value != value:
            current_value = self.value
            self._max_value = value
            self.value = current_value
