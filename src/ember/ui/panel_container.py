import pygame
import itertools
from abc import ABC, abstractmethod
from typing import Union, Optional, Sequence, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.material.material import Material

from .container import Container

from .panel import Panel

from ..common import SequenceElementType

from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember.position import (
    PositionType,
    SequencePositionType,
)

from ..on_event import on_event


class PanelContainer(Container, ABC):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        with self.adding_element(Panel(None, y=0, size=FILL), update=False) as panel:
            self._panel: Panel = panel

    @property
    def panel(self) -> Panel:
        return self._panel

    @panel.setter
    def panel(self, value: Panel) -> None:
        if value is self._panel:
            return
        self.removing_element(self._panel)
        with self.adding_element(value) as panel:
            self._panel = panel

    @property
    def _elements_to_render(self):
        return itertools.chain((self._panel,), super()._elements_to_render)
