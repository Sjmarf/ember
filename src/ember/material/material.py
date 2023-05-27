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

    def __init__(self, alpha: int):
        self._cache: WeakKeyDictionary = WeakKeyDictionary()

        self.alpha: int = alpha
        """
        The transparency of the material, where 0 is fully transparent and 255 is opaque.
        """

    def __repr__(self) -> str:
        return "<Material>"

    def _clear_cache(self) -> None:
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
        return element not in self._cache or self._get(element).get_size() != size

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

    def _get(self, element: "Element") -> Optional[pygame.Surface]:
        """
        Returns the cached surface for an element. None is returned if the surface is not yet cached.
        """
        return self._cache.get(element)

    def draw(
        self,
        element: "Element",
        destination_surface: pygame.Surface,
        pos: tuple[float, float]
    ) -> None:
        """
        Draw the material to a destination surface.
        """
        if element in self._cache:
            destination_surface.blit(self._get(element), pos)

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
        alpha: int,
    ) -> bool:
        """
        Render the material to a surface, which is saved in a cache.
        Returns True if the Surface needed to be re-rendered.
        """
        if self._needs_to_render(element, surface, pos, size):
            log.material.info(self, element, f"Rendering...")
            self._cache[element] = self._render_surface(element, surface, pos, size)
            self._get(element).set_alpha(alpha * self.alpha / 255)
            return True
        else:
            self._get(element).set_alpha(alpha * self.alpha / 255)
            return False


class MaterialWithSizeCache(Material, abc.ABC):
    """ """

    def __init__(self, alpha: int):
        super().__init__(alpha)

        self._size_cache_k: WeakKeyDictionary[
            Element, tuple[float, float]
        ] = WeakKeyDictionary()
        self._size_cache_v: WeakValueDictionary[
            tuple[float, float], Element
        ] = WeakValueDictionary()

    def _clear_cache(self) -> None:
        self._cache.clear()
        self._size_cache_v.clear()
        self._size_cache_k.clear()

    def render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
        alpha: int,
    ) -> bool:
        if self._needs_to_render(element, surface, pos, size):
            if size in self._size_cache_v:
                log.material.info(self, element, f"Reusing size {size}...")
                if self._get(self._size_cache_v[size]).get_size() != size:
                    log.material.info(self, element, f"Rendering...")
                    self._cache[element] = self._render_surface(element, surface, pos, size)
                    
                    other_element = self._size_cache_v[size]
                    if other_element in self._size_cache_k:
                        del self._size_cache_v[self._size_cache_k[other_element]]
                        del self._size_cache_k[other_element]
                        
                    self._size_cache_v[size] = element
                    self._size_cache_k[element] = size
                else:            
                    self._cache[element] = self._cache[self._size_cache_v[size]]
                
            else:
                log.material.info(self, element, f"Rendering...")
                self._cache[element] = self._render_surface(element, surface, pos, size)
                if element in self._size_cache_k:
                    del self._size_cache_v[self._size_cache_k[element]]

                self._size_cache_v[size] = element
                self._size_cache_k[element] = size

            self._get(element).set_alpha(alpha * self.alpha / 255)
            return True
        else:
            self._get(element).set_alpha(alpha * self.alpha / 255)
            return False
