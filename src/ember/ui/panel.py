import pygame
from typing import Union, Optional, Sequence, TYPE_CHECKING

from ..base.element import Element
from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember.position import PositionType, SequencePositionType

from ..common import ColorType

from ..material.material import Material
from ..material.color import Color


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
            self.material.draw(self, surface, rect.topleft, rect.size, alpha)


Panel.w_.default_value = FILL
Panel.h_.default_value = FILL
