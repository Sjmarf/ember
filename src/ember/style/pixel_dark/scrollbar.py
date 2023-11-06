from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember.material.material import Material

from .container import Container

from ember.ui.scrollbar import ScrollBar as _ScrollBar
from ember.ui.interactive_slider import InteractiveSlider
from ember.size import PivotableSize
from ember.material.stretched_surface import StretchedSurface

from ember.common import package

root = package / "style/pixel_dark/assets/bar"


class ScrollBar(_ScrollBar, InteractiveSlider, Container):
    back_material = StretchedSurface(root / "background.png")
    front_material = StretchedSurface(root / "default.png")
    hover_material = StretchedSurface(root / "hover.png")
    focus_material = StretchedSurface(root / "focus.png")
    active_material = StretchedSurface(root / "active.png")

    def _get_front_material(self) -> "Material":
        if self.activated:
            return self.active_material
        if self.focused:
            return self.focus_material
        if self.hovered:
            return self.hover_material
        return self.front_material

    def _get_back_material(self) -> "Material":
        return self.back_material


size = PivotableSize(100, 8)
ScrollBar.center_handle_on_pickup = False
ScrollBar.w.default_value = size
ScrollBar.h.default_value = ~size
del size
