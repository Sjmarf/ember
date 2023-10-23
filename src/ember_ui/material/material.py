import pygame
import abc
from weakref import WeakKeyDictionary, WeakValueDictionary

from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from ember.ui.base.element import Element

from .. import log


class Material(abc.ABC):
    """
    All materials inherit from this class. This base class should not be instantiated.
    """
    UPDATES_EVERY_TICK = False

    def __init__(self, alpha: int):
        self.alpha: int = alpha
        """
        The transparency of the material, where 0 is fully transparent and 255 is opaque.
        """

    @abc.abstractmethod
    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        pass

    def draw(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> None:
        surf = self.render(element, surface, pos, size, alpha)
        if surf is not None:
            surface.blit(surf, pos)


class MaterialWithElementCache(Material):
    """
    Materials that have an element cache inherit from this class.
    This base class should not be instantiated.
    """

    def __init__(self, alpha: int):
        self._cache: WeakKeyDictionary = WeakKeyDictionary()
        super().__init__(alpha)

    def clear_cache(self) -> None:
        self._cache.clear()

    def _needs_to_render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> bool:
        """
        Returns True if a surface needs to be rendered and cached.
        """
        return element not in self._cache or self.get(element).get_size() != size

    def _render_surface(
        self,
        element: Optional["Element"],
        surface: Optional[pygame.Surface],
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> Any:
        """
        Render and return a surface (or the data to be cached) with the given position and size.
        """
        pass

    def get(self, element: "Element") -> Optional[pygame.Surface]:
        """
        Returns the cached surface for an element. None is returned if the surface is not yet cached.
        """
        return self._cache.get(element)

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        """
        Render the material to a surface, which is saved in a cache.
        Returns True if the Surface needed to be re-rendered.
        """
        if self._needs_to_render(element, surface, pos, size):
            log.material.info("Rendering...", element, self)
            self._cache[element] = self._render_surface(element, surface, pos, size)

        new_surface = self.get(element)
        new_surface.set_alpha(alpha * self.alpha / 255)

        return new_surface


class MaterialWithSizeCache(MaterialWithElementCache, abc.ABC):
    """
    Materials that have a size cache in addition to an element cache inherit from this class.
    This base class should not be instantiated.
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)

        self._size_cache_k: WeakKeyDictionary[
            Element, tuple[float, float]
        ] = WeakKeyDictionary()
        self._size_cache_v: WeakValueDictionary[
            tuple[float, float], Element
        ] = WeakValueDictionary()

    def clear_cache(self) -> None:
        self._cache.clear()
        self._size_cache_v.clear()
        self._size_cache_k.clear()

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[int, int],
        size: tuple[int, int],
        alpha: int,
    ) -> Optional[pygame.Surface]:
        if self._needs_to_render(element, surface, pos, size):
            if size in self._size_cache_v:
                log.material.info(f"Reusing size {size}...", element, self)
                if self.get(self._size_cache_v[size]).get_size() != size:
                    log.material.info("Rendering...", element, self)
                    self._cache[element] = self._render_surface(
                        element, surface, pos, size
                    )

                    other_element = self._size_cache_v[size]
                    if other_element in self._size_cache_k:
                        del self._size_cache_v[self._size_cache_k[other_element]]
                        del self._size_cache_k[other_element]

                    self._size_cache_v[size] = element
                    self._size_cache_k[element] = size
                else:
                    self._cache[element] = self._cache[self._size_cache_v[size]]

            else:
                log.material.info("Rendering...", element, self)
                self._cache[element] = self._render_surface(element, surface, pos, size)
                if element in self._size_cache_k:
                    del self._size_cache_v[self._size_cache_k[element]]

                self._size_cache_v[size] = element
                self._size_cache_k[element] = size

        material_surface = self._cache[element]
        material_surface.set_alpha(alpha * self.alpha / 255)
        return material_surface
    