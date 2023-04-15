from typing import Optional

from ember import common as _c

from ember.style.style import Style, MaterialType
from ember.size import SizeType, FIT
from ember.material.material import Material
from ember.style.load_material import load_material

from ember.style.stack_style import StackStyle
from ember.transition.transition import Transition


class ListStyle(Style):
    def __init__(self,
                 highlight_material: MaterialType = None,
                 highlight_focus_material: MaterialType = None,

                 text_width: SizeType = FIT,
                 text_height: SizeType = FIT,

                 stack_style: Optional[StackStyle] = None,

                 material_transition: Optional[Transition] = None
                 ):

        self._highlight_material: Material = load_material(highlight_material, None)
        self._highlight_focus_material: Material = load_material(highlight_focus_material, self._highlight_material)

        self.text_width: SizeType = text_width
        self.text_height: SizeType = text_height

        self.stack_style: Optional[StackStyle] = stack_style

        self.material_transition: Optional[Transition] = material_transition

    def set_as_default(self) -> "ListStyle":
        _c.default_list_style = self
        return self

    highlight_material = property(
        fget=lambda self: self._highlight_material,
        fset=lambda self, value: setattr(self, "_highlight_material", load_material(value, None))
    )

    highlight_focus_material = property(
        fget=lambda self: self._highlight_focus_material,
        fset=lambda self, value: setattr(self, "_highlight_focus_material", load_material(value, None))
    )
