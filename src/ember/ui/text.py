import pygame
from typing import Union, Optional, Literal, TYPE_CHECKING, Sequence
from .. import log
from .. import common as _c
from ..common import ColorType, InheritType, INHERIT
from .base.element import Element
from .base.surfacable import Surfacable

from ..transition.transition import Transition

from ..font.ttf_font import Line

from ..size import FIT, SizeType, SequenceSizeType, SizeMode
from ..position import PositionType, CENTER, SequencePositionType, Position

if TYPE_CHECKING:
    from ..style.text_style import TextStyle
    from .view_layer import ViewLayer


class Text(Surfacable):
    def __init__(
        self,
        text,
        color: Optional[ColorType] = None,
        align: Union[InheritType, Sequence[Position], None] = INHERIT,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
        style: Union["TextStyle", None] = None,
    ):
        # Load the TextStyle object.
        self.set_style(style)

        # Determine which colour to use.
        self._color = color

        self._text: str = text

        self._align: Sequence[Position]
        """
        The alignment of the text within the element.
        """

        self._min_w: float = 0
        self._min_h: float = 0
        self._surface: Optional[pygame.Surface] = None
        self._redraw_next_tick: bool = True

        super().__init__(rect, pos, x, y, size, width, height, default_size=self._style.size, can_focus=False)

        self.lines: list[Line] = []

        self.set_align(align)

    def __repr__(self) -> str:
        if len(self._text) > 15:
            return f"<Text('{self._text[:16]}...')>"
        return f"<Text('{self._text}')>"

    def _get_surface(self, alpha: int = 255) -> pygame.Surface:
        self._surface.set_alpha(alpha)
        return self._surface

    def _draw_surface(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        my_surface: pygame.Surface,
    ) -> None:
        rect = self._int_rect.move(*offset)
        pos = (
            rect.centerx - my_surface.get_width() // 2,
            rect.centery - my_surface.get_height() // 2,
        )

        if self._text:
            if self._color is None:
                new_surface = my_surface.copy()
                self._style.material.render(
                    self, surface, pos, new_surface.get_size(), alpha=255
                )
                new_surface.blit(
                    self._style.material.get(self),
                    (0, 0),
                    special_flags=pygame.BLEND_RGB_ADD,
                )
            else:
                new_surface = my_surface

            surface.blit(
                new_surface,
                (
                    pos[0] - surface.get_abs_offset()[0],
                    pos[1] - surface.get_abs_offset()[1] + self._style.font.y_offset,
                ),
            )

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        super()._update_rect_chain_down(surface, x, y, w, h)
        if (
            self._surface is None
            or self._int_rect.w != self._surface.get_width()
            or self._redraw_next_tick
        ):
            self._update_surface(max_width=w)
            self._redraw_next_tick = False

    @Element._chain_up_decorator
    def _update_rect_chain_up(self):
        self._min_w = (
            self.surface.get_width()
            if self.surface
            else self._style.font.get_width_of_line(self._text)
        )

        self._min_h = self.surface.get_height() if self.surface else self._style.font.line_height

    def _update_surface(self, max_width: float) -> None:
        if max_width == 0:
            max_width = None
        else:
            max_width = round(max_width)
        self._surface, self.lines = self._style.font.render(
            self._text,
            color=self._color if self._color is not None else (0, 0, 0),
            max_width=max_width,
            align=self._align[0],
        )
        log.size.info(
            self,
            f"Surface created of size {self._surface.get_size()}. Starting chain up...",
        )

        with log.size.indent:
            self._update_rect_chain_up()

    def set_text(
        self,
        text: str,
        color: Union[tuple[int, int, int], str, pygame.Color, None] = None,
        transition: Optional[Transition] = None,
    ) -> None:
        """
        Set the text string.
        """
        if text != self._text:
            if transition:
                # It's necessary to create temporary variables here, so that the width and height are accurate
                old_element = self.copy()
                transition = transition._new_element_controller(
                    old_element=old_element, new_element=self
                )
                self._transition = transition

            self._text = text
            self._color = color if color is not None else self._color
            self._redraw_next_tick = True
            with log.size.indent:
                self._update_rect_chain_up()

    def get_line(self, line_index) -> Optional[Line]:
        """
        Get the Line object for a given line index.
        """
        try:
            return self.lines[line_index]
        except IndexError:
            return None

    def get_line_index_from_letter_index(self, letter_index: int) -> int:
        n = 0
        for n, i in enumerate(self.lines):
            if letter_index < i.start_index:
                return n - 1
        return n

    def _set_color(
        self, color: Union[str, tuple[int, int, int], pygame.Color, None]
    ) -> None:
        self.set_color(color)

    def set_color(
        self,
        color: Union[str, tuple[int, int, int], pygame.Color, None] = None,
        transition=None,
    ):
        """
        Set the color of the Text.
        """
        if transition:
            old_element = self.copy()
            transition = transition._new_element_controller(
                old_element=old_element, new_element=self
            )
            self._transition = transition

        self._color = color
        self._redraw_next_tick = True
        with log.size.indent:
            self._update_rect_chain_up()

    def set_width(self, value: SizeType, _update_rect_chain_up=True) -> None:
        super().set_width(value, _update_rect_chain_up)
        self._redraw_next_tick = True
        with log.size.indent:
            self._update_rect_chain_up()

    @property
    def align(self) -> Sequence[Position]:
        return self._align

    @align.setter
    def align(self, align: Union[InheritType, Sequence[Position], None]) -> None:
        self.set_align(align)

    def set_align(self, align: Union[InheritType, Sequence[Position], None]) -> None:
        """
        Set the alignment of the text. Must be 'left', 'center' or 'right'.
        """
        self._align = align
        if align is INHERIT or align is None:
            self._align = self._style.align
        elif isinstance(align, Position):
            self._align = (align, CENTER)
        else:
            self._align = align
        self._redraw_next_tick = True
        log.size.info(self, "Text alignment changed, starting chain up...")
        with log.size.indent:
            self._update_rect_chain_up()

    def _set_style(self, style: Optional["TextStyle"]) -> None:
        self.set_style(style)

    def set_style(self, style: Optional["TextStyle"]) -> None:
        """
        Sets the TextStyle of the Text.
        """
        self._style: "TextStyle" = self._get_style(style)

    text: str = property(fget=lambda self: self._text, doc="The text string.")

    color = property(
        fget=lambda self: self._color, fset=_set_color, doc="The color of the text."
    )

    style: "TextStyle" = property(
        fget=lambda self: self._style, fset=_set_style, doc="The TextStyle of the Text."
    )

    surface: pygame.Surface = property(
        fget=lambda self: self._surface,
        doc="The surface on which the text is drawn. Read-only.",
    )
