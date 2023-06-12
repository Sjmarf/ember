import pygame
import abc
from typing import Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ember.ui.base.element import Element

from ..material import Material

from ...common import ColorType


class Shape(Material, abc.ABC):
    """
    All shape materials inherit from this class. This base class should not be instantiated.
    """

    def __init__(
        self,
        material: Optional[Material] = None,
        color: Optional[ColorType] = None,
        antialias: bool = False,
        outline: int = 0,
        alpha: int = 255,
    ):
        super().__init__(alpha)

        self._antialias: bool = antialias
        self._outline: int = outline

        if color is not None and material is not None:
            raise ValueError("You must provide either a color or material, not both.")

        self._material: Optional[Material] = material
        self._color: Optional[ColorType] = color

    @abc.abstractmethod
    def _create_surface(self, size: tuple[float, float]) -> pygame.Surface:
        pass

    def _update_generic_surface(self):
        self._clear_cache()

    def _needs_to_render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> bool:
        if self._material is not None:
            return (
                self._material._needs_to_render(element, surface, pos, size)
                or element not in self._cache
                or self._cache.get(element).get_size() != size
            )

        elif self._color is not None:
            return (
                element not in self._cache
                or self._cache.get(element).get_size() != size
            )

    def _render_surface(
        self,
        element: Optional["Element"],
        surface: Optional[pygame.Surface],
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> Any:

        surface = self._create_surface(size)

        if self._material:
            surface.blit(
                self._material.get(element),
                (0, 0),
                special_flags=pygame.BLEND_RGB_ADD,
            )
            return surface

        elif self._color:
            surface.fill(self._color, special_flags=pygame.BLEND_RGB_ADD)
        return surface

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
        alpha: int,
    ) -> bool:
        if self._material:
            self._material.render(element, surface, pos, size, alpha)
        return super().render(element, surface, pos, size, alpha)

    def _set_outline(self, outline: int) -> None:
        self.set_outline(outline)

    def set_outline(self, outline: int) -> None:
        """
        "The thickness of the shape outline. If set to 0, the shape will be filled with no outline."
        """
        self._outline = outline
        self._update_generic_surface()

    def _set_antialias(self, value: bool) -> None:
        self.set_antialias(value)

    def set_antialias(self, value: bool) -> None:
        """
        When True, the edges will be anti-aliased.
        """
        self._antialias = value
        self._update_generic_surface()

    outline: int = property(
        fget=lambda self: self._outline,
        fset=_set_outline,
        doc="The thickness of the shape outline. If set to 0, the shape will be filled with no outline.",
    )

    antialias: bool = property(
        fget=lambda self: self._antialias,
        fset=_set_antialias,
        doc="When True, the edges of the shape will be anti-aliased.",
    )
