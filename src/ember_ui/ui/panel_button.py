import pygame
import itertools
from abc import ABC, abstractmethod
from typing import Union, Optional, Sequence, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ember_ui.material.material import Material

from .button import Button

from .panel import Panel

from ..common import SequenceElementType

from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember_ui.position import (
    PositionType,
    SequencePositionType,
)

from ..on_event import on_event


class PanelButton(Button, ABC):
    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        **kwargs
    ):
        super().__init__(
            *elements,
            disabled=disabled,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            **kwargs
        )

        with self.adding_element(Panel(None, y=0, size=FILL), update=False) as panel:
            self._panel: Panel = panel

        self._panel.material = self._get_panel_material()

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

    @on_event()
    def _update_material(self) -> None:
        self._panel.material = self._get_panel_material()

    @abstractmethod
    def _get_panel_material(self) -> "Material":
        ...

    @property
    def _elements_to_render(self):
        return itertools.chain((self._panel,), self._elements)
