import pygame
from typing import Union, Optional, Literal
from .. import log
from .. import common as _c
from .base.element import Element
from .base.surfacable import Surfacable
from ..style.text_style import TextStyle
from ..transition.transition import Transition

from ..font.ttf_font import Line

from ..size import FIT, SizeType, SequenceSizeType
from ..position import PositionType
from ..style.load_style import load as load_style
from ..style.get_style import _get_style


class Text(Surfacable):
    def __init__(
        self,
        text,
        position: PositionType = None,
        size: SequenceSizeType = None,
        width: SizeType = None,
        height: SizeType = None,
        align: Literal["left", "center", "right"] = "center",
        color: Union[str, tuple[int, int, int], pygame.Color, None] = None,
        style: Union[TextStyle, None] = None,
    ):
        # Load the TextStyle object.
        self.set_style(style)

        # Determine which colour to use.
        self._color = color if color else self._style.color

        self._text: str = text
        self._align: Literal["left", "center", "right"] = align

        self._fit_width: float = 0
        self._fit_height: float = 0
        self._surface: Optional[pygame.Surface] = None

        super().__init__(position, size, width, height, default_size=(FIT, FIT), can_focus=False)

        self.lines: list[Line] = []

        self._update_surface()

    def __repr__(self) -> str:
        if len(self._text) > 15:
            return f"<Text('{self._text[:16]}...')>"
        return f"<Text('{self._text}')>"

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255) -> None:
        self._draw_surface(surface, offset, self._get_surface(alpha))

    def _get_surface(self, alpha: int = 255) -> pygame.Surface:
        self._check_for_surface_update(self.rect.w if self.rect.w != 0 else None)
        self._surface.set_alpha(alpha)
        return self._surface

    def _draw_surface(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        my_surface: pygame.Surface,
    ) -> None:
        rect = self._draw_rect.move(*offset)
        pos = (
            rect.centerx - my_surface.get_width() // 2,
            rect.centery - my_surface.get_height() // 2,
        )
        surface.blit(
            my_surface,
            (
                pos[0] - surface.get_abs_offset()[0],
                pos[1] - surface.get_abs_offset()[1] + self._style.font.y_offset,
            ),
        )

    def _update_rect_chain_down(self, surface: pygame.Surface, pos: tuple[float, float], max_size: tuple[float, float],
                                _ignore_fill_width: bool = False, _ignore_fill_height: bool = False) -> None:
        super()._update_rect_chain_down(surface, pos, max_size)
        self._check_for_surface_update(max_width=self.get_abs_width(max_size[0]))

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        if self._surface:
            if self._width.mode == 1:
                self._fit_width = self._surface.get_width()
            if self._height.mode == 1:
                self._fit_height = self._surface.get_height()

    def _check_for_surface_update(self, max_width: Optional[float] = None) -> bool:
        # This is in a separate method because some elements need to call this before its scroll calculations
        if self._surface is None or (
            max_width is not None
            and self._width.mode == 2
            and (round(max_width) != self._surface.get_width())
        ):
            if max_width is not None:
                max_width = round(max_width)
            if self._surface is None:
                log.size.info(self, "Surface is None, creating Surface...")
            else:
                log.size.info(
                    self,
                    f"Width is FILL and max_width '{max_width}' != surface_width "
                    f"'{self._surface.get_width()}' - creating Surface...",
                )
            self._update_surface(max_width=max_width)
            return True
        return False

    def _update_surface(self, max_width: Optional[float] = None) -> None:
        if max_width is None:
            max_width = None if self._width.mode == 1 else self.rect.w
            if max_width == 0:
                log.size.info(
                    self,
                    "Attempted to create Surface but maximum width is 0, deferring.",
                )
                return
        self._surface, self.lines = self._style.font.render(
            self._text,
            col=self._color,
            outline_col=self._style.outline_color,
            max_width=max_width,
            align=self._align if self._align else self._style.align,
        )
        log.size.info(
            self,
            f"Surface created of size {self._surface.get_size()}, starting chain up.",
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
            self._update_surface()

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
        self._update_surface()

    def set_width(self, value: SizeType, _update_rect_chain_up=True) -> None:
        super().set_width(value, _update_rect_chain_up)
        self._update_surface()

    def _set_align(self, align: Literal["left", "center", "right"]) -> None:
        self.set_align(align)

    def set_align(self, align: Literal["left", "center", "right"]) -> None:
        """
        Set the alignment of the text. Must be 'left', 'center' or 'right'.
        """
        self._align = align
        self._update_surface()

    def _set_style(self, style: Optional[TextStyle]) -> None:
        self.set_style(style)

    def set_style(self, style: Optional[TextStyle]) -> None:
        """
        Sets the TextStyle of the Text.
        """
        self._style: TextStyle = _get_style(style, "text")

    text: str = property(fget=lambda self: self._text, doc="The text string.")

    color = property(
        fget=lambda self: self._color, fset=_set_color, doc="The color of the text."
    )

    style: TextStyle = property(
        fget=lambda self: self._style, fset=_set_style, doc="The TextStyle of the Text."
    )

    align: Literal["left", "center", "right"] = property(
        fget=lambda self: self._align,
        fset=_set_align,
        doc="The alignment of the Text. Must be 'left', 'center' or 'right'.",
    )

    surface: pygame.Surface = property(
        fget=lambda self: self._surface,
        doc="The surface on which the text is drawn. Read-only.",
    )
