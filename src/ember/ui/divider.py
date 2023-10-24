import pygame
from typing import Union, Optional, Sequence

from ember.size.size import PivotableSize
from ember.ui.element import Element
from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember.position import PositionType, SequencePositionType

from ..common import ColorType

from ..material.material import Material
from ..material.color import Color, DEFAULT_BLACK_MATERIAL

from ember.trait import Trait


def load_material(material: Union[Material, ColorType, None]) -> Material:
    if isinstance(material, Material) or material is None:
        return material
    return Color(material)


class Divider(Element):
    material = Trait(
        default_value=DEFAULT_BLACK_MATERIAL, load_value_with=load_material
    )

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
        self.material = material
        super().__init__(
            rect=rect, pos=pos, x=x, y=y, size=size, w=w, h=h, can_focus=False
        )

    def __repr__(self) -> str:
        return "<Divider>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self.rect.move([-i for i in surface.get_abs_offset()])
        if self.material is not None:
            self.material.draw(self, surface, rect.topleft, rect.size, alpha)

    def update_ancestry(self, ancestry: list["Element"]) -> None:
        super().update_ancestry(ancestry)
        self._axis = 1 - self.parent._axis


Divider.w.default_value = PivotableSize(FILL, 1)
Divider.h.default_value = PivotableSize(1, FILL)
