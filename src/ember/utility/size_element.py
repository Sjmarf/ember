import pygame
from ..utility.spritesheet import SpriteSheet

def size_element(path, size, edge=(10, 10, 10, 10)) -> pygame.Surface:
    sheet = SpriteSheet(path)
    new_width,new_height = size
    img = pygame.Surface(size, pygame.SRCALPHA)

    e_l, e_r, e_t, e_b = edge
    WIDTH, HEIGHT = sheet.img.get_size()
    # Middle
    try:
        mid = pygame.transform.scale(sheet.image(e_l, e_t, WIDTH - e_l - e_r, HEIGHT - e_t - e_b),
                                     (new_width - e_l - e_r, new_height - e_t - e_b))
        img.blit(mid, (e_l, e_t))
        # Left
        left = pygame.transform.scale(sheet.image(0, e_t, e_l, HEIGHT - e_t - e_b), (e_l, new_height - e_t - e_b))
        img.blit(left, (0, e_t))
        # Right
        right = pygame.transform.scale(sheet.image(WIDTH - e_r, e_t, e_r, HEIGHT - e_t - e_b),
                                       (e_r, new_height - e_t - e_b))
        img.blit(right, (new_width - e_r, e_t))
        # Top
        top = pygame.transform.scale(sheet.image(e_l, 0, WIDTH - e_l - e_r, e_t), (new_width - e_l - e_r, e_t))
        img.blit(top, (e_l, 0))
        # Bottom
        bottom = pygame.transform.scale(sheet.image(e_l, HEIGHT - e_b, WIDTH - e_l - e_r, e_b),
                                        (new_width - e_l - e_r, e_b))
        img.blit(bottom, (e_l, new_height - e_b))
        # Corners
        img.blit(sheet.image(0, 0, e_l, e_t), (0, 0))
        img.blit(sheet.image(WIDTH - e_r, 0, e_r, e_t), (new_width - e_r, 0))
        img.blit(sheet.image(0, HEIGHT - e_b, e_l, e_b), (0, new_height - e_b))
        img.blit(sheet.image(WIDTH - e_r, HEIGHT - e_b, e_r, e_b), (new_width - e_r, new_height - e_b))
    except ValueError:
        raise ValueError(f"size_element size of {size} cannot be smaller than sum of edges {edge}.")

    return img
