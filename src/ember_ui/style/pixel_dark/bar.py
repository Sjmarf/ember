from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ember_ui.material.material import Material

from ember_ui.ui.bar import Bar as _Bar
from ember_ui.font.pixel_font import PixelFont
from ember_ui.material.stretched_surface import StretchedSurface

from ember_ui.common import package
from ember_ui.size.size import PivotableSize
from ember_ui._init import init_task

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
