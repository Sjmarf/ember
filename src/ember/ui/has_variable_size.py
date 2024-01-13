from typing import Union, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from .view_layer import ViewLayer

import pygame

from .has_geometry import HasGeometry
from .. import Trait
from ..position import PositionType, SequencePositionType
from ember.size import Size, FIT, load_size, OptionalSequenceSizeType, SizeType
from ..utility.geometry_vector import GeometryVector
from ember.axis import Axis


class HasVariableSize(HasGeometry):
    def __init__(
        self,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        layer: Optional["ViewLayer"] = None,
        can_focus: bool = False,
    ):
        if rect is not None:
            x, y, w, h = rect[:]

        if size is not None:
            if isinstance(size, Sequence):
                w, h = size
            else:
                w, h = size, size

        self.w = w
        self.h = h

        super().__init__(pos=pos, x=x, y=y, layer=layer, can_focus=can_focus)

    w: Trait[Size] = Trait(
        default_value=FIT,
        on_update=lambda self: self._geometry_trait_modified("w"),
        default_cascade_depth=1,
        load_value_with=load_size,
    )

    h: Trait[Size] = Trait(
        default_value=FIT,
        on_update=lambda self: self._geometry_trait_modified("h"),
        default_cascade_depth=1,
        load_value_with=load_size,
    )

    def get_min_size(self, proposed_size: GeometryVector) -> GeometryVector:
        return GeometryVector(20, 20)

    def _get_dimensions(
        self,
        proposed_size: GeometryVector,
    ) -> GeometryVector:
        min_size = self.get_min_size(proposed_size)

        if self.w.other_value_intent:
            if self.h.other_value_intent:
                raise ValueError(
                    f"{self} size dimensions are reliant on one another, which is disallowed."
                )
            calculated_h = self.h.get(min_size.h, proposed_size.h, 0)
            calculated_w = self.w.get(min_size.w, proposed_size.w, calculated_h)
        elif self.h.other_value_intent:
            calculated_w = self.w.get(min_size.w, proposed_size.w, 0)
            calculated_h = self.h.get(min_size.h, proposed_size.h, calculated_w)
        else:
            calculated_w = self.w.get(min_size.w, proposed_size.w, 0)
            calculated_h = self.h.get(min_size.h, proposed_size.h, 0)

        return GeometryVector(w=calculated_w, h=calculated_h, axis=proposed_size.axis)
