import pygame
from typing import Sequence, Union, Optional, TYPE_CHECKING

from ...position import PositionType, SequencePositionType
from ...size import SizeType, SequenceSizeType, OptionalSequenceSizeType

from ...transition.transition import Transition

from ... import log
from ...common import ColorType

if TYPE_CHECKING:
    from ...material.material import Material
    from ...style.style import Style

from .surfacable import Surfacable


class MultiLayerSurfacable(Surfacable):
    """
    Manages the layer system used by :py:class:`Text<ember.ui.Text>` and :py:class:`Icon<ember.ui.Icon>`.
    This is a base class and should not be instantiated directly.
    """

    def __init__(
        self,
        color: Optional[ColorType] = None,
        material: Optional["Material"] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        default_size: Optional[SequenceSizeType] = None,
        style: Optional["Style"] = None,
        can_focus: bool = True,
    ):
        self._color: Optional[ColorType] = color
        self._material: Optional["Material"] = material

        self._surface_width: int = 0
        self._surface_height: int = 0

        self._surfaces: list[pygame.Surface] = None
        self._layers: list[int] = []
        self._static_surface: Optional[pygame.Surface] = None

        super().__init__(rect, pos, x, y, size, w, h, default_size, style, can_focus)

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
        if self._color is not None:
            # log.mls.info(self, "Applying basic color.")
            surface.fill(self._color, special_flags=pygame.BLEND_RGB_ADD)
            return

        if self._material is not None:
            material = self._material
        elif layer == 1:
            material = self._style.material
        elif layer == 2:
            material = self._style.secondary_material
        else:
            material = self._style.tertiary_material

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
                if self._color is None and self._style.material.UPDATES_EVERY_TICK:
                    log.mls.info(
                        self,
                        "Primary material updates every tick - element is dynamic.",
                    )
                    return False

            if layer == 2:
                if self._style.secondary_material.UPDATES_EVERY_TICK:
                    log.mls.info(
                        self,
                        "Secondary material updates every tick - element is dynamic.",
                    )
                    return False

            if layer == 3:
                if self._style.tertiary_material.UPDATES_EVERY_TICK:
                    log.mls.info(
                        self,
                        "Tertiary material updates every tick - element is dynamic.",
                    )
                    return False

        log.mls.info(self, "Element is static.")
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
        log.mls.info(self, "Generated static surface.")

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
        log.mls.info(self, "Generated dynamic surfaces.")

    @property
    def color(self) -> Optional[ColorType]:
        """
        Get or set the color of the Element. Can be any color type supported by Pygame, or None.
        Specifying a color overwrites all materials specified in the element's Style object. The
        property setter is synonymous with the :py:meth:`set_color<ember.ui.base.MultiLayerSurfacable.set_color>`
        method.
        """
        return self._color

    @color.setter
    def color(self, color: Optional[ColorType]) -> None:
        self.set_color(color)

    def set_color(
        self,
        color: Optional[ColorType] = None,
        transition: Optional[Transition] = None,
    ) -> None:
        """
        Sets the color of the Element. Can be any color type supported by Pygame, or None.
        If None is specified, the materials attributed to the Element's Style object
        will be used. If a color is specified in the Element itself, that color takes
        precendece over *all* Style materials. This method is synonymous with the
        :py:property:`color<ember.ui.base.MultiLayerSurfacable.color>` property setter.
        """
        if transition:
            old_element = self.copy()
            transition = transition._new_element_controller(
                old_element=old_element, new_element=self
            )
            self._transition = transition

        self._color = color

        log.mls.line_break()
        log.mls.info(self, "Color changed, generating surfaces...")

        with log.mls.indent:
            self._generate_surface(self._layers, self._surfaces, reapply=True)

    @property
    def material(self) -> Optional["Material"]:
        """
        Get or set the material of the Element. Specifying a material overwrites all materials
        specified in the element's Style object. The property setter is synonymous with the
        :py:meth:`set_color<ember.ui.base.MultiLayerSurfacable.set_material>` method.
        """
        return self._material

    @material.setter
    def material(self, material: Optional["Material"]) -> None:
        self.set_material(material)

    def set_material(
        self,
        material: Optional["Material"],
        transition: Optional[Transition] = None,
    ) -> None:
        """
        Sets the material of the Element. If None is specified, the materials
        attributed to the Element's Style object will be used. If a material is
        specified in the Element itself, that material takes precendece over *all*
        Style materials. This method is synonymous with the
        :py:property:`material<ember.ui.base.MultiLayerSurfacable.material>` property setter.
        """
        if transition:
            old_element = self.copy()
            transition = transition._new_element_controller(
                old_element=old_element, new_element=self
            )
            self._transition = transition

        self._material = material

        log.mls.line_break()
        log.mls.info(self, "Material changed, generating surfaces...")

        with log.mls.indent:
            self._generate_surface(self._layers, self._surfaces, reapply=True)
