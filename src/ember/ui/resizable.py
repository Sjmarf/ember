import pygame
from typing import Union, Optional, Literal, TYPE_CHECKING, Sequence

from .base.element import Element
from ..material.material import Material
from ..state.state import State, load_background

from ..size import SizeType, OptionalSequenceSizeType, Size
from ..position import (
    PositionType,
    SequencePositionType,
    Position,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
    BasicPosition,
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
        handles: Union[Sequence[BasicPosition], BasicPosition, None] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        min_w: Optional[SizeType] = None,
        min_h: Optional[SizeType] = None,
        max_w: Optional[SizeType] = None,
        max_h: Optional[SizeType] = None,
        style: Optional["ContainerStyle"] = None,
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
            element,
            material,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            style,
        )

        self.resize_limits = (30, 100)
        self.set_min_w(min_w)
        self.set_min_h(min_h)
        self.set_max_w(max_w)
        self.set_max_h(max_h)

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

    def _set_hovering_resizable_edge(self, value: Optional[BasicPosition]) -> None:
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
            self.set_w(int(value))
        if self._handle_hovering is LEFT:
            value = max(
                min(self.rect.w + self.rect.x - _c.mouse_pos[0], self.resize_limits[1]),
                self.resize_limits[0],
            )
            self.set_w(int(value))

        if self._handle_hovering is BOTTOM:
            value = max(
                min(_c.mouse_pos[1] - self.rect.y, self.resize_limits[1]),
                self.resize_limits[0],
            )
            self.set_h(int(value))

        if self._handle_hovering is TOP:
            value = max(
                min(self.rect.h + self.rect.y - _c.mouse_pos[1], self.resize_limits[1]),
                self.resize_limits[0],
            )
            self.set_h(int(value))

        if not self.layer._chain_down_from:
            log.size.info(self, "Resized, starting chain down next tick...")
            self.layer._chain_down_from = self.parent

    def set_min_w(self, value: Optional[int]) -> None:
        """
        Set the minimum width of the Resizable.
        """
        self._min_w: int = value

    def set_min_h(self, value: Optional[int]) -> None:
        """
        Set the minimum height of the Resizable.
        """
        self._min_h: int = value

    def set_max_w(self, value: Optional[int]) -> None:
        """
        Set the maximum width of the Resizable.
        """
        self._min_w: int = value

    def set_max_h(self, value: Optional[int]) -> None:
        """
        Set the maximum height of the Resizable.
        """
        self._min_h: int = value

