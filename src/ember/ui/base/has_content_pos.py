from typing import Optional, Sequence
from ...position import (
    OptionalSequencePositionType,
    PositionType,
    Position,
    DualPosition,
)

from .element import Element


class ContentXMixin(Element):
    def __init__(
        self,
        *args,
        content_x: Optional[PositionType] = None,
        **kwargs,
    ):
        """
        Used to supply the relevant properties and methods to an element that has a 'content_x' parameter.
        """
        self._content_x: Optional[Position] = None
        super().__init__(*args, **kwargs)
        self.set_content_x(content_x, _update=False)

    @property
    def content_x(self) -> Optional[Position]:
        return self._content_x

    @content_x.setter
    def content_x(self, value: Optional[PositionType]) -> None:
        self.set_content_x(value)

    def set_content_x(self, value: Optional[PositionType], _update=True) -> None:
        """
        Set the content_x of the element.
        """
        self._content_x: Optional[Position] = (
            self._style.content_pos[0] if value is None else Position._load(value)
        )
        if _update:
            self._update_rect_chain_up()


class ContentYMixin(Element):
    def __init__(self, *args, content_y: Optional[PositionType] = None, **kwargs):
        """
        Used to supply the relevant properties and methods to an element that has a 'content_y' parameter.
        """
        self._content_y: Optional[Position] = None
        super().__init__(*args, **kwargs)
        self.set_content_y(content_y, _update=False)

    @property
    def content_y(self) -> Optional[Position]:
        return self._content_y

    @content_y.setter
    def content_y(self, value: Optional[PositionType]) -> None:
        self.set_content_y(value)

    def set_content_y(self, value: Optional[PositionType], _update=True) -> None:
        """
        Set the content_x of the element.
        """
        self._content_y: Optional[Position] = (
            self._style.content_pos[1] if value is None else Position._load(value)
        )
        if _update:
            self._update_rect_chain_up()


class ContentPosMixin(ContentXMixin, ContentYMixin):
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

        super().__init__(
            *args,
            content_x=content_x,
            content_y=content_y,
            **kwargs
        )

    @property
    def content_pos(self) -> tuple[Optional[Position], Optional[Position]]:
        return self._content_x, self._content_y

    @content_pos.setter
    def content_pos(self, value: OptionalSequencePositionType) -> None:
        self.set_content_pos(value)

    def set_content_pos(
        self, value: OptionalSequencePositionType, _update=True
    ) -> None:
        if not isinstance(value, Sequence):
            value = value, value

        self.set_content_x(value[0], _update=_update)
        self.set_content_y(value[1], _update=_update)
