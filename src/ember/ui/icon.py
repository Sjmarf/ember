import pygame
from typing import Union, Optional, TYPE_CHECKING, Sequence

from ..common import ColorType, DEFAULT
from .. import log
from ..base.multi_layer_surfacable import MultiLayerSurfacable

from ..size import SizeType, OptionalSequenceSizeType
from ember.position import PositionType, SequencePositionType
from ..font.icon_font import IconFont
from ember.trait.trait import Trait

if TYPE_CHECKING:
    from ..material.material import Material


from ..trait import Trait

class Icon(MultiLayerSurfacable):
    """
    An element that displays an icon (arrow, pause, save, etc).
    """

    font: IconFont = Trait(None)

    def __init__(
        self,
        name: Union[str, pygame.Surface],
        color: Optional[ColorType] = None,
        material: Optional["Material"] = None,
        primary_material: Optional["Material"] = None,
        secondary_material: Optional["Material"] = None,
        tertiary_material: Optional["Material"] = None,
        font: Optional[IconFont] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        self._name: Optional[str] = name
        self.font = font

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
            # Style
        )

    def __repr__(self) -> str:
        return f"<Icon({self._name})>"

    def _build(self) -> None:
        super()._build()
        self.set_icon(self._name, _update=False)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)
        pos = (
            rect.centerx - self._surface_width // 2 - surface.get_abs_offset()[0],
            rect.centery - self._surface_height // 2 - surface.get_abs_offset()[1],
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
            rect.centerx - my_surface.get_width() // 2,
            rect.centery - my_surface.get_height() // 2,
        )

        if self._text:
            surface.blit(
                my_surface,
                (
                    pos[0] - surface.get_abs_offset()[0],
                    pos[1] - surface.get_abs_offset()[1],
                ),
            )

    def _update_min_size(self) -> None:
        self._min_w = self._surface_width
        self._min_h = self._surface_height

    @property
    def name(self) -> Optional[str]:
        """
        Get or set the name of the icon. The 'name' parameter should be a name of an icon included in the
        :py:class:`IconFont<ember.font.IconFont` object. The property setter is synonymous
        """
        return self._name

    @name.setter
    def name(self, name: Union[str, pygame.Surface]) -> None:
        self.set_icon(name)

    def set_icon(self, name: Union[str, pygame.Surface], _update: bool = True) -> None:
        """
        Set the icon image. The 'name' parameter can be a name of an icon included in the :py:class`IconFont<ember.font.IconFont`
        object, or it can be a pygame Surface.

        If it is a Surface, the Surface should contain only black and transparent pixels. Be aware that the Icon will reference
        the original surface, and may modify its pixels. If you don't want this to happen, pass a copy of the Surface instead.

        A color can optionally be specified here too. If no color is specified, the color of the Icon will not change. This method
        is synonymous with the :code:`name` property setter.
        """

        if isinstance(name, str):
            self._name = name
            surfaces = self._font.value.get(name)

        elif isinstance(name, pygame.Surface):
            self._name = None
            surfaces = (name,)

        layers = list(range(1, len(surfaces) + 1))
        self._layers = layers

        self._surface_width, self._surface_height = surfaces[0].get_size()

        with log.mls.indent("Icon changed, generating surfaces...", self):
            self._generate_surface(layers, surfaces)

        if _update:
            self.update_min_size_next_tick()