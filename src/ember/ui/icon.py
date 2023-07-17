import pygame
import inspect
from typing import Union, Optional, TYPE_CHECKING, Sequence

from .. import common as _c
from ..common import ColorType
from .. import log
from .base.element import Element
from .base.styled import StyleMixin
from .base.multi_layer_surfacable import MultiLayerSurfacable

from ..size import SizeType, OptionalSequenceSizeType
from ..position import PositionType, SequencePositionType
from .text import Text

if TYPE_CHECKING:
    from ..style.icon_style import IconStyle

from ..transition.transition import Transition


class Icon(StyleMixin, MultiLayerSurfacable):
    """
    An element that displays an icon (arrow, pause, save, etc). 
    """
    
    def __init__(
        self,
        name: Union[str, pygame.Surface],
        color: Optional[ColorType] = None,
        material: Optional["Material"] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        style: Optional["IconStyle"] = None,
    ):
        self.set_style(style)
        
        self._name: Optional[str] = None

        super().__init__(
           color,
           material,
           rect,
           pos,
           x,
           y,
           size,
           w,
           h,
           style,
           can_focus=False,
       )
             
        self.set_icon(name, _update=False)

    def __repr__(self) -> str:
        return f"<Icon({self._name})>"
    
    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)
        pos = (
                rect.centerx
                - self._surface_width // 2
                - surface.get_abs_offset()[0],
                rect.centery
                - self._surface_height // 2
                - surface.get_abs_offset()[1],
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
                rect.centerx
                - my_surface.get_width() // 2,
                rect.centery
                - my_surface.get_height() // 2,
            )

        if self._text:
            surface.blit(
                my_surface,
                (
                    pos[0] - surface.get_abs_offset()[0],
                    pos[1] - surface.get_abs_offset()[1],
                ),
            )

    @Element._chain_up_decorator
    def _update_rect_chain_up(self) -> None:
        self._min_w = self._surface_width
        self._min_h = self._surface_height

    @property
    def name(self) -> Optional[str]:
        """
        Get or set the name of the icon. The 'name' parameter should be a name of an icon included in the 
        :py:class`IconFont<ember.font.IconFont` object. The property setter is synonymous
        """
        return self._name
    
    @name.setter
    def name(self, name: Union[str, pygame.Surface]) -> None:
        self.set_icon(name)

    def set_icon(
        self,
        name: Union[str, pygame.Surface],
        color: Optional[ColorType] = None,
        transition: Optional[Transition] = None,
        _update: bool = True
    ) -> None:
        """
        Set the icon image. The 'name' parameter can be a name of an icon included in the :py:class`IconFont<ember.font.IconFont`
        object, or it can be a pygame Surface. 
        
        If it is a Surface, the Surface should contain only black and transparent pixels. Be aware that the Icon will reference
        the original surface, and may modify it's pixels. If you don't want this to happen, pass a copy of the Surface instead.
        
        A color can optionally be specified here too. If no color is specified, the color of the Icon will not change. This method
        is synonymous with the :code:`name` property setter.
        """
        
        if transition:
            old_element = self.copy()
            transition = transition._new_element_controller(
                old_element=old_element, new_element=self
            )
            self._transition = transition

        if isinstance(name, str):
            self._name = name
            surfaces = self._style.font.get(name)
            
        elif isinstance(name, pygame.Surface):
            self._name = None
            surfaces = (name, )
        
        layers = list(range(1,len(surfaces)+1))
        self._layers = layers
        
        self._surface_width, self._surface_height = surfaces[0].get_size()

        log.mls.line_break()
        log.mls.info(self, "Icon changed, generating surfaces...")
        with log.mls.indent:
            self._generate_surface(layers, surfaces)
        
        self._color = color if color is not None else self._color
        
        if _update:
            log.size.line_break()
            log.size.info(self, "Icon changed, starting chain up...")
            
            with log.size.indent:        
                self._update_rect_chain_up()
