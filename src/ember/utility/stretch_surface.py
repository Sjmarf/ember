import pygame
from typing import Sequence
from ..utility.spritesheet import SpriteSheet


def stretch_surface(
    surf: pygame.Surface, size: Sequence[int], edge=(10, 10, 10, 10)
) -> pygame.Surface:
    nw, nh = max(0, int(size[0])), max(0, int(size[1]))
    new_surf = pygame.Surface((nw, nh), pygame.SRCALPHA)

    l, r, t, b = edge
    w, h = surf.get_size()

    if l + r > nw:
        l = nw // 2
        r = nw - l

    if t + b > nh:
        t = nh // 2
        b = nh - t

    # Middle
    mid = pygame.transform.scale(
        surf.subsurface(l, t, w - l - r, h - t - b), (nw - l - r, nh - t - b),
    )
    new_surf.blit(mid, (l, t))
    # Left
    left = pygame.transform.scale(surf.subsurface(0, t, l, h - t - b), (l, nh - t - b))
    new_surf.blit(left, (0, t))
    # Right
    right = pygame.transform.scale(
        surf.subsurface(w - r, t, r, h - t - b), (r, nh - t - b)
    )
    new_surf.blit(right, (nw - r, t))
    # Top
    top = pygame.transform.scale(surf.subsurface(l, 0, w - l - r, t), (nw - l - r, t))
    new_surf.blit(top, (l, 0))
    # Bottom
    bottom = pygame.transform.scale(
        surf.subsurface(l, h - b, w - l - r, b), (nw - l - r, b)
    )
    new_surf.blit(bottom, (l, nh - b))
    # Corners
    new_surf.blit(surf.subsurface(0, 0, l, t), (0, 0))
    new_surf.blit(surf.subsurface(w - r, 0, r, t), (nw - r, 0))
    new_surf.blit(surf.subsurface(0, h - b, l, b), (0, nh - b))
    new_surf.blit(surf.subsurface(w - r, h - b, r, b), (nw - r, nh - b))

    return new_surf
