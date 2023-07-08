import pygame
from typing import Optional, Sequence

from .style import Style
from ..font import IconFont
from .. import common as _c
from ..common import MaterialType
from ..common import ColorType
from ..ui.icon import Icon

from ..material.material import Material
from ..material.color import Color
from ..size import SizeType, SequenceSizeType, FIT
from ..position import Position
from ..font.variant import TextVariant


class IconStyle(Style):
    _ELEMENT = Icon

    def __init__(
        self,
        size: SequenceSizeType = (FIT, FIT),
        width: SizeType = None,
        height: SizeType = None,
        font: IconFont = None,
        color: ColorType = "white",
        secondary_color: Optional[ColorType] = None,
        tertiary_color: Optional[ColorType] = None,
        material: Optional[MaterialType] = None,
        secondary_material: Optional[MaterialType] = None,
        tertiary_material: Optional[MaterialType] = None
        
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Icon if no size is specified in the Icon constructor.
        """

        self.material: Material = Color(color) if material is None else material
        
        self.secondary_material: Material
        if secondary_material is None:
            if secondary_color is None:
                self.secondary_material = self.material
            else:
                self.secondary_material = Color(secondary_color)
        else:
            self.secondary_material = secondary_material
            
        self.tertiary_material: Material
        if tertiary_material is None:
            if tertiary_color is None:
                self.tertiary_material = self.secondary_material
            else:
                self.tertiary_material = Color(tertiary_color)
        else:
            self.tertiary_material = tertiary_material        

        self.font: IconFont = font
