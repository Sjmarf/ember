import pygame
from typing import Union, Optional, Literal, TYPE_CHECKING, Sequence

from .base.element import Element
from ..material.material import Material
from ..state.state import State, load_background

from ..size import FIT, FILL, SizeType, SequenceSizeType
from ..position import (
    PositionType,
    SequencePositionType,
    Position,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
    CardinalPosition,
)

if TYPE_CHECKING:
    from ..style.container_style import ContainerStyle

from .. import common as _c
from .. import log
from .box import Box


class Resizable(Box):
    """
    A single element container that can be resized with the mouse. Experimental.
    """

    def __init__(
        self,
        element: Optional[Element],
        material: Union["State", Material, None] = None,
        handles: Union[Sequence[CardinalPosition], CardinalPosition, None] = None,
        resize_limits: tuple[int, int] = (50, 300),
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
    ):
        self.handles: Sequence[CardinalPosition] = (
            [handles] if isinstance(handles, Position) else handles
        )
        """
        Specify which edge(s) of the Box can be resized by clicking and dragging with the mouse.
        """

        self.resize_limits: tuple[int, int] = resize_limits
        """
        Specify limits that the user cannot resize the Box beyond.
        """

        self._handle_hovering: Optional[CardinalPosition] = None
        self._resizing: bool = False

        super().__init__(
            element,
            material,
            rect,
            pos,
            x,
            y,
            size,
            width,
            height,
            style,
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
        if RIGHT in self.handles:
            if (
                self.rect.collidepoint(self.rect.x, _c.mouse_pos[1])
                and self.rect.right - 2 < _c.mouse_pos[0] < self.rect.right + 2
            ):
                return self._set_hovering_resizable_edge(RIGHT)

        if LEFT in self.handles:
            if (
                self.rect.collidepoint(self.rect.x, _c.mouse_pos[1])
                and self.rect.left - 2 < _c.mouse_pos[0] < self.rect.left + 2
            ):
                return self._set_hovering_resizable_edge(LEFT)

        if TOP in self.handles:
            if (
                self.rect.collidepoint(_c.mouse_pos[0], self.rect.y)
                and self.rect.top - 2 < _c.mouse_pos[1] < self.rect.top + 2
            ):
                return self._set_hovering_resizable_edge(TOP)

        if BOTTOM in self.handles:
            if (
                self.rect.collidepoint(_c.mouse_pos[0], self.rect.y)
                and self.rect.bottom - 2 < _c.mouse_pos[1] < self.rect.bottom + 2
            ):
                return self._set_hovering_resizable_edge(BOTTOM)

        self._set_hovering_resizable_edge(None)

    def _set_hovering_resizable_edge(self, value: Optional[CardinalPosition]) -> None:
        if value == self._handle_hovering:
            return

        if self._handle_hovering is None:
            if value in {LEFT, RIGHT}:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENS)

        elif value is None:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self._handle_hovering = value

    def _resize(self) -> None:
        if self._handle_hovering is RIGHT:
            value = max(
                min(_c.mouse_pos[0] - self.rect.x, self.resize_limits[1]),
                self.resize_limits[0],
            )
            self.set_width(value)
        if self._handle_hovering is LEFT:
            value = max(
                min(self.rect.w + self.rect.x - _c.mouse_pos[0], self.resize_limits[1]),
                self.resize_limits[0],
            )
            self.set_width(value)

        if self._handle_hovering is BOTTOM:
            value = max(
                min(_c.mouse_pos[1] - self.rect.y, self.resize_limits[1]),
                self.resize_limits[0],
            )
            self.set_height(value)

        if self._handle_hovering is TOP:
            value = max(
                min(self.rect.h + self.rect.y - _c.mouse_pos[1], self.resize_limits[1]),
                self.resize_limits[0],
            )
            self.set_height(value)

        if not self.layer._chain_down_from:
            log.size.info(self, "Resized, starting chain down next tick...")
            self.layer._chain_down_from = self.parent
