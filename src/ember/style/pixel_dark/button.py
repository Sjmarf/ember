from ember.ui.panel_button import PanelButton

from ember.material.material import Material
from ember.material.stretched_surface import StretchedSurface

from .container import Container

from ember.common import package

from ember.on_event import on_event

root = package / "style/pixel_dark/assets/button"

from ember.ui.has_geometry import HasGeometry
from ember.event import CLICKEDDOWN, CLICKEDUP


class Button(PanelButton, Container):
    default_material = StretchedSurface(root / "default.png")
    hover_material = StretchedSurface(root / "hover.png")
    click_material = StretchedSurface(root / "click.png")
    focus_material = StretchedSurface(root / "focus.png")
    focus_click_material = StretchedSurface(root / "focus_click.png")
    disabled_material = StretchedSurface(root / "disabled.png")

    def _get_panel_material(self) -> "Material":
        if self.disabled:
            return self.disabled_material
        if self.focused and self.clicked:
            return self.focus_click_material
        if self.focused:
            return self.focus_material
        if self.clicked:
            return self.click_material
        if self.hovered:
            return self.hover_material
        return self.default_material

    @on_event(CLICKEDDOWN)
    def _update_content_y_down(self) -> None:
        self.cascading[HasGeometry.y] += 1

    @on_event(CLICKEDUP)
    def _update_content_y_up(self) -> None:
        self.cascading[HasGeometry.y] -= 1


Button.w.default_value = 70
Button.h.default_value = 21
