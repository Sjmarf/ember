import math
import pygame
from .. import common as _c
from ..common import (
    FocusType,
    FOCUS_FIRST,
    FOCUS_LAST,
    SequenceElementType,
)
from typing import Union, Optional, Sequence, TYPE_CHECKING

from ember.base.stack import Stack
from ..base.content_pos import ContentPos
from ember.base.content_size import ContentSize
from .. import log

from ember.base.element import Element


from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)
from ..size import SizeType, OptionalSequenceSizeType, FILL

class ZStack(ContentPos, ContentSize, Stack):

    default_w = FILL
    default_h = FILL
    default_focus_on_entry = FOCUS_LAST

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        focus_on_entry: Optional[FocusType] = FOCUS_LAST,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
    ):
        super().__init__(
            # Stack
            *elements,
            focus_on_entry=focus_on_entry,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            # ContentPos
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            # ContentSize
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
        )

    def __repr__(self) -> str:
        return f"<ZStack({len(self._elements)} elements)>"

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if self.layer.element_focused is self:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        element = None
        if (
            direction
            in {
                _c.FocusDirection.IN,
                _c.FocusDirection.IN_FIRST,
                _c.FocusDirection.SELECT,
            }
            and self.focus_on_entry is FOCUS_LAST
        ):
            for i in reversed(self._elements):
                if i._can_focus:
                    element = i
                    break

        elif self.focus_on_entry is FOCUS_FIRST:
            for i in self._elements:
                if i._can_focus:
                    element = i
                    break

        elif direction == _c.FocusDirection.OUT:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        elif direction == _c.FocusDirection.FORWARD:
            if self.layer.element_focused is not self._elements[-1]:
                index = self._elements.index(self.layer.element_focused)
                element = self._elements[index + 1]

        elif direction == _c.FocusDirection.BACKWARD:
            if self.layer.element_focused is not self._elements[0]:
                index = self._elements.index(self.layer.element_focused)
                element = self._elements[index - 1]

        else:
            target = (
                self.layer.element_focused.rect.topleft
                if self.layer.element_focused is not None
                else (0, 0)
            )
            closest_distance = math.inf
            for i in self._elements:
                if not i._can_focus:
                    continue
                if direction == _c.FocusDirection.RIGHT:
                    if i.rect.x <= self.layer.element_focused.rect.x:
                        continue
                elif direction == _c.FocusDirection.LEFT:
                    if i.rect.x >= self.layer.element_focused.rect.x:
                        continue
                elif direction == _c.FocusDirection.UP:
                    if i.rect.y >= self.layer.element_focused.rect.y:
                        continue
                elif direction == _c.FocusDirection.DOWN:
                    if i.rect.y <= self.layer.element_focused.rect.y:
                        continue

                dist = math.sqrt(
                    (i.rect.x - target[0]) ** 2 + (i.rect.y - target[1]) ** 2
                )

                if dist < closest_distance:
                    element = i
                    closest_distance = dist

        if element is None:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(f"-> child {element}.")
            return element._focus_chain(_c.FocusDirection.IN)
