from ember.ui.switch import Switch as _Switch
from .text import Text
from .button import Button

from ember.material.material import Material
from ember.material.stretched_surface import StretchedSurface
from ember.size import PivotableSize

from ember.common import package
from ember._init import init_task

root = package / "style/pixel_dark/assets/switch"


class Switch(_Switch):
    text_class = Text

    base_material = StretchedSurface(root / "base.png")
    default_material = StretchedSurface(root / "default.png")
    hover_material = StretchedSurface(root / "hover.png")
    focus_material = StretchedSurface(root / "focus.png")
    disabled_material = StretchedSurface(root / "disabled.png")

    def _get_front_material(self) -> "Material":
        if self.disabled:
            return self.disabled_material
        if self.focused:
            return self.focus_material
        if self.hovered:
            return self.hover_material
        return self.default_material

    def _get_back_material(self) -> "Material":
        return self.base_material


Switch.w.default_value = PivotableSize(26, 14)
Switch.h.default_value = PivotableSize(14, 26)
