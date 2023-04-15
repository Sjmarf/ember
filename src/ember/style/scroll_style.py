from typing import Optional

from .. import common as _c
from .style import Style
from ..size import SizeType

from .load_material import load_material, MaterialType
from ..material.material import Material

from ..transition.transition import Transition


class ScrollStyle(Style):
    def __init__(self,
                 material: MaterialType = None,
                 focus_material: MaterialType = None,
                 focus_child_material: MaterialType = None,

                 base_material: MaterialType = None,
                 handle_material: MaterialType = None,
                 handle_hover_material: MaterialType = None,
                 handle_click_material: MaterialType = None,

                 scrollbar_size: int = 3,

                 padding: int = 10,
                 scroll_speed: int = 5,

                 over_scroll: tuple[int, int] = (0,0),

                 material_transition: Optional[Transition] = None,
                 handle_material_transition: Optional[Transition] = None):

        self._material: Material = load_material(material, None)
        self._focus_material: Material = load_material(focus_material, None)
        self._focus_child_material: Material = load_material(focus_child_material, self._focus_material)

        self._base_material: Material = load_material(base_material, None)
        self._handle_material: Material = load_material(handle_material, None)
        self._handle_hover_material: Material = load_material(handle_hover_material, self._handle_material)
        self._handle_click_material: Material = load_material(handle_click_material, self._handle_hover_material)

        self.scrollbar_size: int = scrollbar_size
        self.padding: int = padding
        self.scroll_speed: int = scroll_speed
        self.over_scroll: tuple[int, int] = over_scroll

        self.material_transition: Optional[Transition] = material_transition
        self.handle_material_transition: Optional[Transition] = handle_material_transition

    def set_as_default(self) -> "ScrollStyle":
        _c.default_scroll_style = self
        return self

    material = property(
        fget=lambda self: self._material,
        fset=lambda self, value: setattr(self, "_material", load_material(value, None))
    )

    focus_material = property(
        fget=lambda self: self._focus_material,
        fset=lambda self, value: setattr(self, "_focus_material", load_material(value, None))
    )

    focus_child_material = property(
        fget=lambda self: self._focus_child_material,
        fset=lambda self, value: setattr(self, "_focus_child_material", load_material(value, None))
    )

    base_material = property(
        fget=lambda self: self._base_material,
        fset=lambda self, value: setattr(self, "_base_material", load_material(value, None))
    )

    handle_material = property(
        fget=lambda self: self._handle_material,
        fset=lambda self, value: setattr(self, "_handle_material", load_material(value, None))
    )

    handle_hover_material = property(
        fget=lambda self: self._handle_hover_material,
        fset=lambda self, value: setattr(self, "_handle_hover_material", load_material(value, None))
    )

    handle_click_material = property(
        fget=lambda self: self._handle_click_material,
        fset=lambda self, value: setattr(self, "_handle_click_material", load_material(value, None))
    )