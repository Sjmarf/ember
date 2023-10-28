import pygame
import ember
from ember.style import pixel_dark as ui

pygame.init()

WIDTH = 300
HEIGHT = 200
ZOOM = 3

screen = pygame.display.set_mode((WIDTH*ZOOM, HEIGHT*ZOOM))
display = pygame.Surface((WIDTH, HEIGHT))
clock = pygame.time.Clock()

ember.init()
ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

with ember.View() as view:
    with ui.VStack:
        button = ui.Button("Click me!")
        ui.Switch()
        ui.Slider(value=0.2)

running = True
while running:
    _mouse = pygame.mouse.get_pos()
    mouse_pos = (_mouse[0] // ZOOM, _mouse[1] // ZOOM)

    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            running = False

        if event.type == ember.CLICKEDDOWN:
            if event.element is button:
                print("Clicked!")

    display.fill(ui.background_color)
    view.update(display)
    screen.blit(pygame.transform.scale(display, (WIDTH*ZOOM, HEIGHT*ZOOM)), (0, 0))

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
