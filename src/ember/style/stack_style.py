from typing import Optional
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


from .. import common as _c
from .style import Style, MaterialType

from .load_material import load_material
from ..material.material import Material
from ..transition.transition import Transition


class StackStyle(Style):
    def __init__(self,
                 material: MaterialType = None,
                 focus_material: MaterialType = None,
                 focus_child_material: MaterialType = None,

                 spacing: Optional[int] = None,
                 min_spacing: int = 6,
                 focus_self: bool = False,
                 focus_on_entry: Literal['closest', 'first'] = 'closest',

                 align_elements_v: Literal["left", "center", "right"] = "center",
                 align_elements_h: Literal["top", "center", "bottom"] = "center",

                 material_transition: Optional[Transition] = None
                 ):

        self._material: Material = load_material(material, None)
        self._focus_material: Material = load_material(focus_material, self._material)
        self._focus_child_material: Material = load_material(focus_child_material, self._focus_material)

        self.spacing: Optional[int] = spacing
        self.min_spacing: int = min_spacing
        self.focus_self: bool = focus_self
        self.focus_on_entry: Literal['closest', 'first'] = focus_on_entry

        self.align_elements_v: Literal["left", "center", "right"] = align_elements_v
        self.align_elements_h: Literal["top", "center", "bottom"] = align_elements_h

        self.material_transition: Optional[Transition] = material_transition

    def set_as_default(self) -> "StackStyle":
        _c.default_stack_style = self
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
