import itertools
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember.material.material import Material

from .container import Container

from .panel import Panel

from ember.on_event import on_event
from .panel_container import PanelBox

class HandledElement(Container, ABC):
    def __init__(
        self,
        *args,
        back_panel: Panel | None = None,
        handle: PanelBox | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if back_panel is None:
            back_panel = Panel(None)
        if handle is None:
            handle = PanelBox(panel=Panel(None))

        with self.adding_element(back_panel, update=False) as panel:
            self._back_panel: Panel = panel

        with self.adding_element(handle, update=False) as handle:
            self._handle: PanelBox = handle

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
    def handle(self) -> Panel:
        return self._handle

    @handle.setter
    def handle(self, value: Panel) -> None:
        if value is self._handle:
            return
        self.removing_element(self._handle)
        with self.adding_element(value) as panel:
            self._handle = panel

    @property
    def _child_elements(self):
        return itertools.chain(
            (self._back_panel, self._handle), super()._child_elements
        )


class UpdatingHandleElement(HandledElement, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._back_panel.material = self._get_back_material()
        self._handle.panel.material = self._get_front_material()

    @on_event()
    def _update_panel_material(self) -> None:
        self._back_panel.material = self._get_back_material()
        self._handle.panel.material = self._get_front_material()

    @abstractmethod
    def _get_front_material(self) -> "Material":
        ...

    @abstractmethod
    def _get_back_material(self) -> "Material":
        ...
