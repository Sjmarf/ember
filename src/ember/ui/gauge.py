import pygame
from abc import ABC, abstractmethod
from typing import Union, Optional, Sequence, TYPE_CHECKING, Generator, Type

from ember import log
from ..common import SequenceElementType, DEFAULT
from ..event import VALUEMODIFIED

from ..size import SizeType, OptionalSequenceSizeType, FIT
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)

from ember.base.element import Element

if TYPE_CHECKING:
    pass

class Gauge(Element):
    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        value: Optional[float] = 0,
        min_value: float = 0,
        max_value: float = 1,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        **kwargs,
    ):
        super().__init__(
            # MultiElementContainer
            *elements,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            **kwargs,
        )
        
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
        if self._progress != (
            progress := pygame.math.clamp(
                (value - self._min_value) / (self._max_value - self._min_value), 0, 1
            )
        ):
            self._progress = progress
            with log.size.indent(f"Modifying gauge value (progress set to {progress})..."):
                event = pygame.event.Event(VALUEMODIFIED, element=self)
                self._post_event(event)
            
    @property
    def progress(self) -> float:
        return self._progress
    
    @progress.setter
    def progress(self, value: float) -> None:
        if value != self._progress:
            with log.size.indent(f"Set gauge progress to {value}..."):
                self._progress = pygame.math.clamp(value, 0, 1)
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