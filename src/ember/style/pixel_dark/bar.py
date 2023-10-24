from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember.material.material import Material

from ember.ui.bar import Bar as _Bar
from ember.font.pixel_font import PixelFont
from ember.material.stretched_surface import StretchedSurface

from ember.common import package
from ember.size.size import PivotableSize
from ember._init import init_task

root = package / "style/pixel_dark/assets/bar"


class Bar(_Bar):
    back_material = StretchedSurface(root / "background.png")
    front_material = StretchedSurface(root / "default.png")

    def _get_front_material(self) -> "Material":
        return self.front_material

    def _get_back_material(self) -> "Material":
        return self.back_material


size = PivotableSize(70, 11)
Bar.w.default_value = size
Bar.h.default_value = ~size
