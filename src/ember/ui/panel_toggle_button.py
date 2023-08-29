from typing import Optional

from .panel_button import PanelButton
from .toggle_button import ToggleButton

from ..common import MaterialType

from ..material import Material
from ..material.blank import Blank

from ..utility.load_material import load_material


class PanelToggleButton(ToggleButton, PanelButton):
    active_material: Material = Blank()
    active_hover_material: Material = Blank()
    active_click_material: Material = Blank()

    @classmethod
    def add_materials(
        cls,
        default_material: Optional[MaterialType] = None,
        hover_material: Optional[MaterialType] = None,
        click_material: Optional[MaterialType] = None,
        active_material: Optional[MaterialType] = None,
        active_hover_material: Optional[MaterialType] = None,
        active_click_material: Optional[MaterialType] = None,
        focus_material: Optional[MaterialType] = None,
        focus_click_material: Optional[MaterialType] = None,
        disabled_material: Optional[MaterialType] = None,
    ) -> None:
        super().add_materials(
            default_material,
            hover_material,
            click_material,
            focus_material,
            focus_click_material,
            disabled_material,
        )

        cls.active_material = load_material(
            active_material, cls.active_material, cls.click_material
        )
        cls.active_hover_material = load_material(
            active_hover_material, cls.active_hover_material, cls.active_material
        )
        cls.active_click_material = load_material(
            active_click_material, cls.active_click_material, cls.active_hover_material
        )

    def _update_panel_material(self) -> None:
        if self.disabled:
            self.panel.material = self.disabled_material

        elif self.clicked:
            if self.focused:
                self.panel.material = self.focus_click_material
            elif self.active:
                self.panel.material = self.active_click_material
            else:
                self.panel.material = self.click_material

        elif self.focused:
            self.panel.material = self.focus_material

        elif self.hovered:
            if self.active:
                self.panel.material = self.active_hover_material
            else:
                self.panel.material = self.hover_material

        elif self.active:
            self.panel.material = self.active_material
        else:
            self.panel.material = self.default_material
