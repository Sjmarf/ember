import pygame
from typing import Union, Optional, Literal, Sequence

from .style import Style
from ..font import Font, BaseFont
from .. import common as _c
from ..common import MaterialType
from ..common import ColorType
from ..ui.text import Text
from ..ui.icon import Icon

from ..material.material import Material
from ..material.color import Color
from ..size import SizeType, SequenceSizeType, FIT
from ..position import CENTER, SequencePositionType, Position


class TextStyle(Style):
    _ELEMENT = Text
    _SECONDARY_ELEMENTS = [Icon]

    def __init__(
        self,
        size: SequenceSizeType = (FIT, FIT),
        width: SizeType = None,
        height: SizeType = None,
        font: Optional[BaseFont] = None,
        # variant: str = "regular",
        align: SequencePositionType = CENTER,
        color: ColorType = (255, 255, 255),
        # secondary_color: ColorType = (0, 0, 0),
        material: MaterialType = None,
        # secondary_material: MaterialType = None,
    ):
        self.size: tuple[SizeType, SizeType] = self.load_size(size, width, height)
        """
        The size of the Element if no size is specified in the Element constructor.
        """
        # self.variant: str = variant

        self.material: Material = material if material is not None else Color(color)
        # self.secondary_material: Material = (
        #     secondary_material
        #     if secondary_material is not None
        #     else Color(secondary_color)
        # )

        if not isinstance(align, Sequence):
            align = (align, align)

        self.align: Sequence[Position] = align
        """
        The alignment of the text within the element.
        """

        self.font: BaseFont = (
            Font(pygame.font.SysFont("arial", 20)) if font is None else font
        )
