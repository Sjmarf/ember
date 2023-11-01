import itertools
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember.material.material import Material

from .container import Container

from .panel import Panel

from ..size import FILL

from ember.on_event import on_event


class TwoPanelContainer(Container, ABC):
    def __init__(
        self,
        *args,
        back_panel: Panel | None = None,
        front_panel: Panel | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if back_panel is None:
            back_panel = Panel(None)
        if front_panel is None:
            front_panel = Panel(None)

        with self.adding_element(back_panel, update=False) as panel:
            self._back_panel: Panel = panel
        with self.adding_element(front_panel, update=False) as panel:
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
        return itertools.chain(
            (self._back_panel, self._front_panel), super()._elements_to_render
        )


class UpdatingTwoPanelContainer(TwoPanelContainer, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._back_panel.material = self._get_back_material()
        self._front_panel.material = self._get_front_material()

    @on_event()
    def _update_panel_material(self) -> None:
        self._back_panel.material = self._get_back_material()
        self._front_panel.material = self._get_front_material()

    @abstractmethod
    def _get_front_material(self) -> "Material":
        ...

    @abstractmethod
    def _get_back_material(self) -> "Material":
        ...
