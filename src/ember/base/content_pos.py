from typing import Optional, Sequence
from ember.position import (
    OptionalSequencePositionType,
    PositionType,
    Position,
    DualPosition,
    load_position,
)

from ember.base.element import Element
from ember.trait import new_trait


class ContentX(Element):
    content_x, content_x_ = new_trait(None)

    def __init__(self, *args, content_x: Optional[PositionType] = None, **kwargs):
        self.content_x = load_position(content_x)
        super().__init__(*args, **kwargs)


class ContentY(Element):
    content_y, content_y_ = new_trait(None)

    def __init__(self, *args, content_y: Optional[PositionType] = None, **kwargs):
        self.content_y = load_position(content_y)
        super().__init__(*args, **kwargs)


class ContentPos(ContentX, ContentY):
    def __init__(
        self,
        *args,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        **kwargs,
    ):
        if isinstance(content_pos, DualPosition):
            content_pos = content_pos.x, content_pos.y
        elif not isinstance(content_pos, Sequence):
            content_pos = content_pos, content_pos

        content_x = content_x if content_x is not None else content_pos[0]
        content_y = content_y if content_y is not None else content_pos[1]

        super().__init__(*args, content_x=content_x, content_y=content_y, **kwargs)

    @property
    def content_pos(self) -> tuple[Optional[Position], Optional[Position]]:
        return self.content_x, self.content_y

    @content_pos.setter
    def content_pos(self, value: OptionalSequencePositionType) -> None:
        if not isinstance(value, Sequence):
            value = value, value

        self.content_x = value[0]
        self.content_y = value[1]
