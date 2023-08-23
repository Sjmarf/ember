import pygame
from typing import Union, Optional, Sequence, TYPE_CHECKING

from ..base.element import Element
from ..size import SizeType, OptionalSequenceSizeType, FILL
from ember.position import PositionType, SequencePositionType

if TYPE_CHECKING:
    from ..material.material import Material


class Panel(Element):
    default_w = FILL
    default_h = FILL

    def __init__(
        self,
        material: Optional["Material"] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        self.material: Optional["Material"] = material
        super().__init__(rect, pos, x, y, size, w, h, can_focus=False)

    def __repr__(self) -> str:
        return "<Panel>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self.rect.move([-i for i in surface.get_abs_offset()])
        if self.material is not None:
            self.material.draw(self, surface, rect.topleft, rect.size, alpha)
