import pygame
import ember

pygame.init()

WIDTH = 801
HEIGHT = 600
ZOOM = 3

WIDTH += ZOOM - WIDTH % ZOOM
HEIGHT += ZOOM - WIDTH % ZOOM

screen = pygame.display.set_mode((WIDTH, HEIGHT))

display = pygame.Surface((WIDTH / ZOOM, HEIGHT / ZOOM), pygame.SRCALPHA)
clock = pygame.time.Clock()

ember.set_clock(clock)
ember.set_display_zoom(ZOOM)

ui = ember.style.PixelDark()

with ember.View() as view:
    with ember.HStack(w=250, h=ember.FIT, spacing=4):
        with ui.Button(size=ember.FILL):
            ui.Text("One fish, two fish, red fish, blue fish", w=ember.FILL)
        with ember.VStack(spacing=4, w=100, content_w=ember.FILL) as stack:
            ui.Button("Hello")
            with ember.HStack(spacing=4):
                ui.Button("World", w=ember.FILL)
                ui.HSwitch(w=ember.FILL, h=23)
            with ui.ToggleButton() as play_button:
                ui.Icon("triangle_right")


is_running = True
while is_running:

    for event in pygame.event.get():
        view.event(event)
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == ember.BUTTONDOWN:
            if event.element is play_button:
                with ember.animation.EaseInOut(0.5):
                    stack.w = 150 if event.element.active else 100

    display.fill(ui.background_color)
    view.update(display)
    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))

    clock.tick(120)
    pygame.display.flip()

pygame.quit()
