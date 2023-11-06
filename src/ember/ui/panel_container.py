import pygame
import itertools
from abc import ABC

from .container import Container

from .panel import Panel
from .box import Box


class PanelContainer(Container, ABC):
    def __init__(self, *args, panel: Panel | None = None, **kwargs):
        super().__init__(*args, **kwargs)

        if panel is None:
            panel = Panel(None)

        with self.adding_element(panel, update=False) as panel:
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


class PanelBox(PanelContainer, Box):
    ...
