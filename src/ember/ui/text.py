import pygame
from typing import Union, Optional, TYPE_CHECKING, Sequence
from .. import log
from ..common import ColorType
from ..base.multi_layer_surfacable import MultiLayerSurfacable

from ..font.base_font import Font
from ..font.line import Line
from ..font.variant import TextVariant

from ..size import SizeType, OptionalSequenceSizeType, FitSize
from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
    CENTER,
)

if TYPE_CHECKING:
    from ..material.material import Material

from ember.trait import Trait


class Text(MultiLayerSurfacable):
    """
    An Element that displays some text.
    """

    variant: TextVariant = Trait(
        (), on_update=lambda self: self._update_surface()
    )

    font = Trait(None)

    def __init__(
        self,
        text: str = "",
        color: Optional[ColorType] = None,
        material: Optional["Material"] = None,
        primary_material: Optional["Material"] = None,
        secondary_material: Optional["Material"] = None,
        tertiary_material: Optional["Material"] = None,
        variant: Union[TextVariant, Sequence[TextVariant], None] = None,
        font: Optional[Font] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        self._text: str = text

        if isinstance(variant, Sequence):
            variant = tuple(variant)
        elif variant is not None:
            variant = (variant,)

        self.variant = variant
        self.font = font

        self._redraw_next_tick: bool = True

        super().__init__(
            # MultiLayerSurfacable
            color=color,
            material=material,
            primary_material=primary_material,
            secondary_material=secondary_material,
            tertiary_material=tertiary_material,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            can_focus=False,
        )

        self.lines: list[Line] = []

    def __repr__(self) -> str:
        if len(self._text) > 15:
            return f"<Text('{self._text[:16]}...', len={len(self._text)})>"
        return f"<Text('{self._text}')>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self.rect.move(*offset)

        # Temporary until we reimplement a content trait system
        content_y = CENTER
        
        pos = (
            rect.x - surface.get_abs_offset()[0] + (0.5 if self.rect.w % 2 == 1 else 0),
            rect.y
            + content_y.get(rect.h, self._surface_height)
            - (0.5 if self.rect.h % 2 == 0 else 0)
            - surface.get_abs_offset()[1],
        )

        self._render_surfaces(surface, pos, alpha)

    def _draw_surface(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        my_surface: pygame.Surface,
    ) -> None:
        rect = self.rect.move(*offset)
        
        # Temporary until we reimplement a content trait system
        content_y = CENTER
        
        pos = (
            rect.x,
            rect.y + content_y.get(rect.h, my_surface.get_height()),
        )

        if self._text:
            surface.blit(
                my_surface,
                (
                    pos[0] - surface.get_abs_offset()[0] + self._font.value.offset[0],
                    pos[1] - surface.get_abs_offset()[1] + self._font.value.offset[1],
                ),
            )

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        if (
            self._static_surface is None
            or self._int_rect.w != self._static_surface.get_width()
            or self._redraw_next_tick
        ):
            log.size.info(
                "Text received its first update, generating surfaces...", self
            )
            log.mls.line_break()
            with log.mls.indent(
                "Text received its first update, generating surfaces...", self
            ):
                self._update_surface()
            self._redraw_next_tick = False

    def _update_min_size(self) -> None:
        self._min_size.w = (
            self._surface_width
            if self._surface_width
            else self.font.get_width_of_line(self._text, self.variant)
        )

        self._min_size.h = (
            self._surface_height if self._surface_height else self.font.line_height
        )

    def _update_surface(self, _update: bool = True) -> None:
        """
        Recreate the text surfaces and apply materials to them.
        """
        max_width = (
            None if self.rect.w == 0 or isinstance(self.w, FitSize) else self.rect.w
        )
        
        surfaces, self.lines = self.font.render(
            self._text,
            variant=self.variant,
            max_width=max_width,
            align=CENTER,
        )

        if (self._surface_width, self._surface_height) != (
            size := surfaces[0].get_size()
        ):
            self._surface_width, self._surface_height = size
        else:
            _update = False

        self._layers = self.font.get_layers(self.variant)

        self._generate_surface(self._layers, surfaces)

        if self._static_surface:
            log.size.info(
                f"Static surface created of size ({self._surface_width}, {self._surface_height}).",
                self,
            )
        else:
            log.size.info(
                f"Dynamic surface list populated with {len(self._surfaces)} surfaces of size ({self._surface_width}, {self._surface_height}).",
                self,
            )
        if _update:
            self.update_min_size_next_tick()

    # def set_w(self, value: SizeType, _update=True) -> None:
    #     log.size.line_break()
    #     log.mls.line_break()
    #     log.size.info(self, "Text width was changed, generating surfaces...")
    #     log.mls.info(self, "Text width was changed, generating surfaces...")
    #     with log.mls.indent, log.size.indent:
    #         self._update_surface(_update=_update)

    @property
    def text(self) -> str:
        """
        Get or set the text string. The property setter is synonymous with the
        :py:meth:`set_text<ember.ui.Text.set_text>` method.
        """
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self.set_text(text)

    def set_text(self, text: str) -> None:
        """
        Set the text string. This method is synonymous with the
        :py:property:`text<ember.ui.Text.text>` property setter.
        """
        if text != self._text:
            self._text = text

            log.size.line_break()
            log.mls.line_break()
            with log.mls.indent(
                "Text was set, generating surfaces...", self
            ), log.size.indent("Text was set, generating surfaces...", self):
                self._update_surface()

    def get_line(self, line_index: int) -> Optional[Line]:
        """
        Get the Line object for a given line index.
        """
        try:
            return self.lines[line_index]
        except IndexError:
            return None

    def get_line_index_from_letter_index(self, letter_index: int) -> int:
        """
        Get the line index for a given letter index.
        """
        n = 0
        for n, i in enumerate(self.lines):
            if letter_index < i.start_index:
                return n - 1
        return n
