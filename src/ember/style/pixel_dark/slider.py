from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember.material.material import Material

from .bar import Bar
from ember.ui.slider import Slider as _Slider
from ember.material.stretched_surface import StretchedSurface

from ember.common import package
from ember._init import init_task

root = package / "style/pixel_dark/assets/bar"


class Slider(_Slider, Bar):
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

