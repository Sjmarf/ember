from ember_ui.ui.panel_toggle_button import PanelToggleButton

from ember_ui.material.stretched_surface import StretchedSurface
from ember_ui.material.material import Material

from .button import Button

from ember_ui.common import package
from ember_ui._init import init_task

root = package / "style/pixel_dark/assets/button"


class ToggleButton(Button, PanelToggleButton):
    
    active_material = StretchedSurface(root / "active.png")
    active_hover_material = StretchedSurface(root / "active_hover.png")
    active_clicked_material = StretchedSurface(root / "active_click.png")

    def _get_panel_material(self) -> "Material":
        if self.disabled:
            return self.disabled_material
        if self.active:
            if self.clicked:
                return self.active_clicked_material
            if self.hovered:
                return self.active_hover_material
            return self.active_material
        return super()._get_panel_material()

