import pygame
from typing import Sequence
from ..utility.spritesheet import SpriteSheet


def stretch_surface(
    surf: pygame.Surface, size: Sequence[int], edge=(10, 10, 10, 10)
) -> pygame.Surface:
    nw, nh = size
    new_surf = pygame.Surface(size, pygame.SRCALPHA)

    l, e_r, t, b = edge
    w, h = surf.get_size()
    # Middle
    try:
        mid = pygame.transform.scale(
            surf.subsurface(l, t, w - l - e_r, h - t - b),
            (nw - l - e_r, nh - t - b),
        )
        new_surf.blit(mid, (l, t))
        # Left
        left = pygame.transform.scale(
            surf.subsurface(0, t, l, h - t - b), (l, nh - t - b)
        )
        new_surf.blit(left, (0, t))
        # Right
        right = pygame.transform.scale(
            surf.subsurface(w - e_r, t, e_r, h - t - b), (e_r, nh - t - b)
        )
        new_surf.blit(right, (nw - e_r, t))
        # Top
        top = pygame.transform.scale(
            surf.subsurface(l, 0, w - l - e_r, t), (nw - l - e_r, t)
        )
        new_surf.blit(top, (l, 0))
        # Bottom
        bottom = pygame.transform.scale(
            surf.subsurface(l, h - b, w - l - e_r, b), (nw - l - e_r, b)
        )
        new_surf.blit(bottom, (l, nh - b))
        # Corners
        new_surf.blit(surf.subsurface(0, 0, l, t), (0, 0))
        new_surf.blit(surf.subsurface(w - e_r, 0, e_r, t), (nw - e_r, 0))
        new_surf.blit(surf.subsurface(0, h - b, l, b), (0, nh - b))
        new_surf.blit(surf.subsurface(w - e_r, h - b, e_r, b), (nw - e_r, nh - b))

    except ValueError:
        raise ValueError(
            f"size_element size of {size} values cannot be smaller than sum of edges {edge}."
        )

    return new_surf
