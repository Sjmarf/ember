import pygame
import math
from typing import Union, Optional, Sequence

from ember.ui.element import Element
from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember.position import PositionType, SequencePositionType

from ..common import ColorType

from ..material.material import Material
from ..material.color import Color


def _round(value):
    if value - int(value) == 0.5:
        return math.ceil(value)
    return round(value)

class Panel(Element):
    def __init__(
        self,
        material: Union["Material", ColorType, None] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        self.material: Optional["Material"] = (
            material
            if isinstance(material, Material) or material is None
            else Color(material)
        )
        super().__init__(rect, pos, x, y, size, w, h, can_focus=False)

    def __repr__(self) -> str:
        return "<Panel>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self.rect.move([-i for i in surface.get_abs_offset()])
        if self.material is not None:
            # print(rect)
            # w = int(rect.w) + (math.ceil(rect.right) - int(rect.x) - int(rect.w))
            # h = int(rect.h) + (math.ceil(rect.bottom) - int(rect.y) - int(rect.h))
            x = int(rect.x)
            y = int(rect.y)
            w = int(rect.right - x)
            h = int(rect.bottom - y)
            # 10.6 + 4.4 = 15
            # 10, 4
            # round(15 - int(10.6))
            self.material.draw(self, surface, (x,y), (w,h), alpha)
            # print((int(rect.x), int(rect.y)), (w, h))


Panel.w.default_value = FILL
Panel.h.default_value = FILL
