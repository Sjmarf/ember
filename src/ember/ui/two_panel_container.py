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


class TwoPanelContainer(Container, ABC):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
            
        with self.adding_element(Panel(None, y=0, size=FILL), update=False) as panel:
            self._back_panel: Panel = panel
        with self.adding_element(Panel(None), update=False) as panel:
            self._front_panel: Panel = panel

    @property
    def back_panel(self) -> Panel:
        return self._back_panel

    @back_panel.setter
    def back_panel(self, value: Panel) -> None:
        if value is self._back_panel:
            return
        self.removing_element(self._back_panel)
        with self.adding_element(value) as panel:
            self._back_panel = panel
            
    @property
    def front_panel(self) -> Panel:
        return self._front_panel

    @front_panel.setter
    def front_panel(self, value: Panel) -> None:
        if value is self._front_panel:
            return
        self.removing_element(self._front_panel)
        with self.adding_element(value) as panel:
            self._front_panel = panel
    

    @property
    def _elements_to_render(self):
        return itertools.chain((self._back_panel, self._front_panel), super()._elements_to_render)
