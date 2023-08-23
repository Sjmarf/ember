from abc import ABC

import pygame
from typing import Sequence, Union, Optional, TYPE_CHECKING

from ember.position import PositionType, SequencePositionType
from ember.size import SizeType, OptionalSequenceSizeType


from ember import log
from ember.common import ColorType
from ember.material.color import Color, DEFAULT_BLACK_MATERIAL

if TYPE_CHECKING:
    from ember.material.material import Material

from .surfacable import Surfacable

from ember.trait import new_trait


class MultiLayerSurfacable(Surfacable):
    """
    Manages the layer system used by :py:class:`Text<ember.ui.Text>` and :py:class:`Icon<ember.ui.Icon>`.
    This is a base class and should not be instantiated directly.
    """

    primary_material, primary_material_ = new_trait(
        DEFAULT_BLACK_MATERIAL,
        on_update=lambda self: self._material_trait_update_callback(),
    )

    secondary_material, secondary_material_ = new_trait(
        DEFAULT_BLACK_MATERIAL,
        on_update=lambda self: self._material_trait_update_callback(),
    )

    tertiary_material, tertiary_material_ = new_trait(
        DEFAULT_BLACK_MATERIAL,
        on_update=lambda self: self._material_trait_update_callback(),
    )

    def __init__(
        self,
        color: Optional[ColorType] = None,
        material: Optional["Material"] = None,
        primary_material: Optional["Material"] = None,
        secondary_material: Optional["Material"] = None,
        tertiary_material: Optional["Material"] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        can_focus: bool = True,
    ):
        if color is not None:
            material = Color(color)

        self.primary_material = primary_material if primary_material else material
        self.secondary_material = secondary_material if secondary_material else material
        self.tertiary_material = tertiary_material if tertiary_material else material

        self._surface_width: int = 0
        self._surface_height: int = 0

        self._surfaces: list[pygame.Surface] = []
        self._layers: list[int] = []
        self._static_surface: Optional[pygame.Surface] = None

        super().__init__(
            rect=rect, pos=pos, x=x, y=y, size=size, w=w, h=h, can_focus=can_focus
        )

    def _material_trait_update_callback(self) -> None:
        log.mls.line_break()
        with log.mls.indent("Material changed, generating surfaces...", self):
            self._generate_surface(self._layers, self._surfaces, reapply=True)

    def _render_surfaces(
        self, surface: pygame.Surface, pos: tuple[int, int], alpha: int
    ) -> None:
        """
        Renders the surface layers.
        """
        if self._static_surface is not None:
            self._static_surface.set_alpha(alpha)
            surface.blit(self._static_surface, pos)

        for layer, surf in zip(self._layers, self._surfaces):
            new_surf = surf.copy()
            self._apply_material_to_surface(new_surf, layer, surface, pos)
            surface.blit(new_surf, pos)

    def _get_surface(self, alpha: int = 255) -> pygame.Surface:
        surface = self._static_surface.copy()
        surface.set_alpha(alpha)

        for layer, surf in zip(self._layers, self._surfaces):
            new_surf = surf.copy()
            self._apply_material_to_surface(new_surf, layer, surface, pos)
            surface.blit(new_surf, (0, 0))

        return surface

    def _apply_material_to_surface(
        self,
        surface: pygame.Surface,
        layer: int,
        destination: pygame.Surface,
        pos: tuple[int, int],
        update_mode: bool = False,
    ) -> None:
        """
        Determines which material should be applied to a given surface, and applies it.
        If :code:`update_mode` is :code:`True`, the material will not be applied to the surface
        if the material updates every tick. If :code:`update_mode` is :code:`False`, the material
        will *only* be applied to the surface if the material updates every tick.
        """

        if layer == 0:
            # log.mls.info(self, "Layer=0, no material applied.")
            return

        if layer == 1:
            material = self.primary_material
        elif layer == 2:
            material = self.secondary_material
        else:
            material = self.tertiary_material

        if material.UPDATES_EVERY_TICK == update_mode:
            # log.mls.info(self, f"Material updates_every_tick = {update_mode}; no material applied.")
            return

        # log.mls.info(self, f"Layer={layer}, applying style material.")
        material.render(self, destination, pos, destination.get_size(), alpha=255)
        surface.blit(
            material.get(self),
            (0, 0),
            special_flags=pygame.BLEND_RGB_ADD,
        )

    def _generate_surface(
        self,
        layers: Sequence[int],
        surfaces: Sequence[pygame.Surface],
        reapply: bool = False,
    ) -> None:
        """
        Given a list of surfaces and their layer codes, generates the required surfaces for rendering.
        If :code:`reapply` is :code:`False`, the surfaces will be assumed to be black. If :code:`True`,
        the function will ensure that the surfaces are black before material application.
        """
        self._surfaces = surfaces
        if self._get_is_static(layers):
            self._generate_static_surface(layers, surfaces, reapply=reapply)
        else:
            self._generate_dynamic_surfaces(layers, surfaces, reapply=reapply)

    def _get_is_static(self, layers: Sequence[int]) -> bool:
        """
        Determine whether the element is 'static'. A MultiLayerSurfacable element is static when
        none of its materials need to update every tick.
        """
        for layer in layers:
            if layer == 1:
                if self.primary_material.UPDATES_EVERY_TICK:
                    log.mls.info(
                        "Primary material updates every tick - element is dynamic.",
                        self,
                    )
                    return False

            if layer == 2:
                if self.secondary_material.UPDATES_EVERY_TICK:
                    log.mls.info(
                        "Secondary material updates every tick - element is dynamic.",
                        self,
                    )
                    return False

            if layer == 3:
                if self.tertiary_material.UPDATES_EVERY_TICK:
                    log.mls.info(
                        "Tertiary material updates every tick - element is dynamic.",
                        self,
                    )
                    return False

        log.mls.info("Element is static.", self)
        return True

    def _generate_static_surface(
        self,
        layers: Sequence[int],
        surfaces: Sequence[pygame.Surface],
        reapply: bool = False,
    ) -> None:
        """
        Generates a static surface from the Element's materials. This static surface is generated once, and
        is simply blitted every tick when the Element is rendered.

        If :code:`reapply` is :code:`False`, the surfaces will be assumed to be black. If :code:`True`,
        the function will ensure that the surfaces are black before material application.
        """
        for n, (layer, surf) in enumerate(zip(layers, surfaces)):
            if reapply:
                surf.fill(0xFFFFFF, special_flags=pygame.BLEND_RGB_SUB)
            self._apply_material_to_surface(surf, layer, surf, (0, 0), update_mode=True)

            if n == 0:
                self._static_surface = surf
            else:
                self._static_surface.blit(surf, (0, 0))
        log.mls.info("Generated static surface.", self)

    def _generate_dynamic_surfaces(
        self, surfaces: Sequence[pygame.Surface], reapply: bool = False
    ) -> None:
        """
        Generates a list of surfaces. If the material for a surface needs to update every tick, the surface is
        left black and the material is applied in
        :py:meth:`_render_surfaces<ember.ui.base.MultiLayerSurfacable._render_surfaces>`.
        If the material does not need to update every tick, the material is applied here.

        If :code:`reapply` is :code:`False`, the surfaces will be assumed to be black. If :code:`True`,
        the function will ensure that the surfaces are black before material application.
        """
        self._static_surface = None
        for layer, surf in zip(self._layers, surfaces):
            if reapply:
                surf.fill(0xFFFFFF, special_flags=pygame.BLEND_RGB_SUB)
            self._apply_material_to_surface(surf, layer, surf, (0, 0), update_mode=True)
        log.mls.info("Generated dynamic surfaces.", self)
