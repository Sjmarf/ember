import pygame
import math
from typing import Union, Optional, Literal, TYPE_CHECKING, Sequence
from .. import log
from .. import common as _c
from ..common import ColorType, InheritType, INHERIT
from .base.element import Element
from .base.multi_layer_surfacable import MultiLayerSurfacable
from .base.has_content_pos import HasContentPos

from ..transition.transition import Transition

from ..font.line import Line
from ..font.variant import TextVariant

from ..size import FIT, SizeType, SequenceSizeType, SizeMode, Size, OptionalSequenceSizeType
from ..position import (
    PositionType,
    CENTER,
    SequencePositionType,
    Position,
    OptionalSequencePositionType,
)

if TYPE_CHECKING:
    from ..style.text_style import TextStyle
    from ..material.material import Material
    from .view_layer import ViewLayer


class Text(MultiLayerSurfacable, HasContentPos):
    """
    An Element that displays some text.
    """
    
    def __init__(
        self,
        text: str,
        color: Optional[ColorType] = None,
        material: Optional["Material"] = None,
        variant: Union[TextVariant, Sequence[TextVariant], None] = None,
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
        style: Optional["TextStyle"] = None,
    ):

        self._style: TextStyle

        self.set_style(style)

        self._text: str = text
        self._variant: Sequence[TextVariant] = (
            variant if isinstance(variant, Sequence) else (variant,)
        )  

        self._redraw_next_tick: bool = True

        MultiLayerSurfacable.__init__(
            self,
            color,
            material,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            can_focus=False,
        )

        HasContentPos.__init__(self, content_pos, content_x, content_y)

        self.lines: list[Line] = []

        log.size.line_break()
        log.size.info(self, "Text created, starting chain up...")
        
        with log.size.indent:
            self._update_rect_chain_up()

    def __repr__(self) -> str:
        if len(self._text) > 15:
            return f"<Text('{self._text[:16]}...', length={len(self._text)})>"
        return f"<Text('{self._text}')>"

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)
        pos = (
            rect.x
            - surface.get_abs_offset()[0],
            rect.y
            + self._content_y.get(self.rect.h, self._surface_height)
            - surface.get_abs_offset()[1]
        )

        self._render_surfaces(surface, pos, alpha)

    def _draw_surface(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int],
        my_surface: pygame.Surface,
    ) -> None:
        rect = self._int_rect.move(*offset)
        pos = (
            rect.x,
            rect.y + self._content_y.get(self.rect.h, my_surface.get_height()),
        )

        if self._text:
            surface.blit(
                my_surface,
                (
                    pos[0] - surface.get_abs_offset()[0] + self._style.font.offset[0],
                    pos[1] - surface.get_abs_offset()[1] + self._style.font.offset[1],
                ),
            )

    def _update_rect_chain_down(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        super()._update_rect_chain_down(surface, x, y, w, h)
        if (
            self._static_surface is None
            or self._int_rect.w != self._static_surface.get_width()
            or self._redraw_next_tick
        ):
            log.mls.line_break()
            log.mls.info(self, "Text recieved its first update, generating surfaces...")
            with log.mls.indent:            
                self._update_surface()
            self._redraw_next_tick = False

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        self._min_w = (
            self._surface_width
            if self._surface_width
            else self._style.font.get_width_of_line(self._text, self._variant)
        )

        self._min_h = (
            self._surface_height
            if self._surface_height
            else self._style.font.line_height
        )

    def _update_surface(self, _update: bool = True) -> None:
        """
        Recreate the text surfaces and apply materials to them.
        """
        max_width = None if self._int_rect.w == 0 or self._active_w.mode == SizeMode.FIT else self._int_rect.w

        surfaces, self.lines = self._style.font.render(
            self._text,
            variant=self._variant,
            max_width=max_width,
            align=self._content_x,
        )

        if (self._surface_width, self._surface_height) != (
            size := surfaces[0].get_size()
        ):
            self._surface_width, self._surface_height = size
        else:
            _update = False

        self._layers = self._style.font.get_layers(self._variant)
    
        self._generate_surface(self._layers, surfaces)
        
        if self._static_surface:
            log.size.info(
                self,
                f"Static surface created of size ({self._surface_width}, {self._surface_height}).",
            )
        else:
            log.size.info(
                self,
                f"Dynamic surface list populated with {len(self._surfaces)} surfaces of size ({self._surface_width}, {self._surface_height}).",
            )
        if _update:
            log.size.line_break()
            log.size.info(self, "Text updated, starting chain up.")
            with log.size.indent:
                self._update_rect_chain_up()
            
    
    def set_w(self, value: SizeType, _update=True) -> None:
        self._w: Size = Size._load(value)
        log.size.line_break()
        log.mls.line_break()
        log.size.info(self, "Text width was changed, generating surfaces...")
        log.mls.info(self, "Text width was changed, generating surfaces...")
        with log.mls.indent, log.size.indent:
            self._update_surface(_update=_update)    
        
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
        
    def set_text(
        self,
        text: str,
        color: Optional[ColorType] = None,
        transition: Optional[Transition] = None,
    ) -> None:
        """
        Set the text string. A color can optionally be specified here too. If no color
        is specified, the color will not change. This method is synonymous with the 
        :py:property:`text<ember.ui.Text.text>` property setter.
        """
        if text != self._text:
            if transition:
                old_element = self.copy()
                transition = transition._new_element_controller(
                    old_element=old_element, new_element=self
                )
                self._transition = transition

            self._text = text
            self._color = color if color is not None else self._color
            
            log.size.line_break()
            log.mls.line_break()
            log.size.info(self, "Text was set, generating surfaces...")
            log.mls.info(self, "Text was set, generating surfaces...")
            with log.mls.indent, log.size.indent:
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
