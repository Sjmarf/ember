import pygame
from typing import Union, Optional, Sequence

from ember_ui.ui.element import Element

from ..size import SizeType, OptionalSequenceSizeType, ResizableSize
from ember_ui.position import (
    PositionType,
    SequencePositionType,
    Position,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
    BasicPosition,
)

from .. import common as _c
from .box import Box


class Resizable(Box):
    """
    A subclass of Box that can be resized using the mouse.
    """

    def __init__(
        self,
        element: Optional[Element] = None,
        handles: Union[Sequence[BasicPosition], BasicPosition, None] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None
    ):
        self.handles: Sequence[BasicPosition] = (
            [handles] if isinstance(handles, Position) else handles
        )
        """
        Specify which edge(s) of the Box can be resized by clicking and dragging with the mouse.
        """

        self._handle_hovering: Optional[BasicPosition] = None
        self._resizing: bool = False

        super().__init__(
            element=element,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h
        )

    def _update(self) -> None:
        super()._update()
        if self.handles and not self._resizing:
            self._is_hovering_resizable_edge()

    def _event(self, event: pygame.event.Event) -> bool:
        if self._handle_hovering:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._resizing = True
                return True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._resizing = False
                return True

            elif event.type == pygame.MOUSEMOTION and self._resizing:
                self._resize()
                return True

        return super()._event(event)

    def _is_hovering_resizable_edge(self) -> None:
        for handle in self.handles:
            if handle is RIGHT:
                if (
                    self.rect.collidepoint(self.rect.x, _c.mouse_pos[1])
                    and self.rect.right - 2 < _c.mouse_pos[0] < self.rect.right + 2
                ):
                    return self._set_hovering_resizable_edge(RIGHT)

            if handle is LEFT:
                if (
                    self.rect.collidepoint(self.rect.x, _c.mouse_pos[1])
                    and self.rect.left - 2 < _c.mouse_pos[0] < self.rect.left + 2
                ):
                    return self._set_hovering_resizable_edge(LEFT)

            if handle is TOP:
                if (
                    self.rect.collidepoint(_c.mouse_pos[0], self.rect.y)
                    and self.rect.top - 2 < _c.mouse_pos[1] < self.rect.top + 2
                ):
                    return self._set_hovering_resizable_edge(TOP)

            if handle is BOTTOM:
                if (
                    self.rect.collidepoint(_c.mouse_pos[0], self.rect.y)
                    and self.rect.bottom - 2 < _c.mouse_pos[1] < self.rect.bottom + 2
                ):
                    return self._set_hovering_resizable_edge(BOTTOM)

        self._set_hovering_resizable_edge(None)

    def _set_hovering_resizable_edge(self, value: Optional[BasicPosition]) -> None:
        if value == self._handle_hovering:
            return

        if self._handle_hovering is None:
            if value in [LEFT, RIGHT]:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)

        elif value is None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self._handle_hovering = value

    def _resize(self) -> None:
        if self._handle_hovering is RIGHT:

            if isinstance(self.w, ResizableSize):
                self.w._set_value(int(_c.mouse_pos[0] - self.rect.x))
            else:
                raise _c.Error("Non-resizable side on resizable edge.")

        if self._handle_hovering is LEFT:

            if isinstance(self.w, ResizableSize):
                self.w._set_value(int(self.rect.w + self.rect.x - _c.mouse_pos[0]))
            else:
                raise _c.Error("Non-resizable side on resizable edge.")

        if self._handle_hovering is BOTTOM:
            if isinstance(self.h, ResizableSize):
                self.h._set_value(int(_c.mouse_pos[1] - self.rect.y))
            else:
                raise _c.Error("Non-resizable side on resizable edge.")

        if self._handle_hovering is TOP:
            if isinstance(self.h, ResizableSize):
                self.h._set_value(int(self.rect.h + self.rect.y - _c.mouse_pos[1]))
            else:
                raise _c.Error("Non-resizable side on resizable edge.")

        self.update_min_size_next_tick()
        self.update_rect_next_tick()
