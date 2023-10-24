import pygame
import pygame.gfxdraw


def draw_circle(
    surface: pygame.Surface,
    pos: tuple[float, float],
    radius: int,
    antialias: bool,
    outline: int,
) -> None:
    if antialias:
        scale = 4
        circle = pygame.Surface(
            (radius * scale * 2, radius * scale * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            circle,
            (0, 0, 0),
            (radius * scale, radius * scale),
            radius * scale,
            outline * scale,
        )
        surface.blit(
            pygame.transform.smoothscale(circle, (radius * 2, radius * 2)),
            (pos[0] - radius, pos[1] - radius),
        )
    else:
        pygame.draw.circle(surface, (0, 0, 0), pos, radius, outline)


def draw_ellipse(
    surface: pygame.Surface, rect: pygame.rect.RectType, antialias: bool, outline: int
) -> None:
    if antialias:
        scale = 4
        new_rect = [i * scale for i in rect]
        ellipse = pygame.Surface(new_rect[2:], pygame.SRCALPHA)
        pygame.draw.ellipse(ellipse, (0, 0, 0), new_rect, outline * scale)
        surface.blit(pygame.transform.smoothscale(ellipse, rect[2:]), rect)
    else:
        pygame.draw.ellipse(surface, (0, 0, 0), rect, outline)


def draw_arc(
    surface: pygame.Surface,
    pos: tuple[float, float],
    radius: int,
    antialias: bool,
    outline: int,
    start_angle: float,
    stop_angle: float,
) -> None:
    if outline:
        if antialias:
            scale = 4
            circle = pygame.Surface(
                (radius * scale * 2, radius * scale * 2), pygame.SRCALPHA
            )
            pygame.draw.arc(
                circle,
                (0, 0, 0),
                (0, 0, radius * scale * 2, radius * scale * 2),
                start_angle,
                stop_angle,
                outline * scale,
            )
            surface.blit(
                pygame.transform.smoothscale(circle, (radius * 2, radius * 2)),
                (pos[0] - radius, pos[1] - radius),
            )
        else:
            pygame.draw.arc(
                surface,
                (0, 0, 0),
                (pos[0] - radius, pos[1] - radius, radius * 2, radius * 2),
                start_angle,
                stop_angle,
                outline,
            )
    else:
        draw_circle(surface, pos, radius, antialias, 0)
