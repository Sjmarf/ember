import pygame
from typing import Union, Optional, Sequence

from .style import Style
from ..font import Font, BaseFont
from ..common import MaterialType
from ..common import ColorType
from ..ui.text import Text

from ..material.material import Material
from ..material.color import Color
from ..size import SizeType, SequenceSizeType, FIT
from ember.position.position import CENTER, SequencePositionType, Position
from ..font.variant import TextVariant

class TextStyle(Style):
    _ELEMENT = Text

    def __init__(
        self,
        size: SequenceSizeType = (FIT, FIT),
        width: SizeType = None,
        height: SizeType = None,
        content_pos: SequencePositionType = CENTER,
        font: Union[BaseFont, pygame.Font, None] = None,
        variant: Union[TextVariant, Sequence[TextVariant]] = (),
        color: ColorType = "black",
        secondary_color: Optional[ColorType] = None,
        tertiary_color: Optional[ColorType] = None,
        material: Optional[MaterialType] = None,
        secondary_material: Optional[MaterialType] = None,
        tertiary_material: Optional[MaterialType] = None
        
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Text if no size is specified in the Text constructor.
        """
        
        self._variant: Sequence[TextVariant] = variant if isinstance(variant, Sequence) else (variant,)

        if not isinstance(content_pos, Sequence):
            content_pos = (content_pos, content_pos)

        self.content_pos: Sequence[Position] = content_pos
        """
        The alignment of the text within the Text element.
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

        self.font: BaseFont = (
            Font(pygame.font.SysFont("arial", 20)) if font is None else font
        )

