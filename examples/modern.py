import pygame
import os
import sys
from typing import Type

try:
    import ember
except ModuleNotFoundError:
    path = os.getcwd().replace(f"examples", "")
    sys.path.append(path)
    import ember

pygame.init()
screen = pygame.display.set_mode((1280, 831), pygame.SCALED)
wallpaper = pygame.image.load("wallpaper.png").convert_alpha()
clock = pygame.time.Clock()

ember.init(clock)

frame_counter = ember.Text("")


# Create materials
def avg_col(adjustment, shape: Type[ember.material.shape.Shape] = ember.material.shape.RoundedRect):
    return shape(
        material=ember.material.AverageColor(hsv_adjustment=adjustment))


default_material = avg_col((0, 0, 20))
hover_material = avg_col((0, 0, 30))

# Create styles
button_style = ember.style.ButtonStyle(
    material=default_material,
    hover_material=hover_material,
    click_material=avg_col((0, -20, 50)),
    focus_material=avg_col((0, -20, 50)),
    focus_click_material=avg_col((0, -30, 50)),
    material_transition=ember.transition.SurfaceFade(duration=0.2)
)
button_style.set_as_default()

text_field_style = ember.style.TextFieldStyle(
    default_image=avg_col((0, 30, -20)),
    active_image=avg_col((0, 30, -10)),
    padding=30,
    fade_width=30,
    text_align="left",
    material_transition=ember.transition.SurfaceFade(duration=0.2)
)

text_field_style.set_as_default()

slider_style = ember.style.SliderStyle(
    base_image=avg_col((0, 40, -20), shape=ember.material.shape.Capsule),
    default_image=avg_col((0, -40, 40), shape=ember.material.shape.Capsule),
    hover_image=avg_col((0, -50, 60), shape=ember.material.shape.Capsule),
    click_image=ember.material.shape.Capsule(color=pygame.Color((255, 255, 255)))
)

slider_style.set_as_default()

big_text = ember.style.TextStyle(font=ember.font.Font(pygame.font.SysFont("arial", 40)))

content = ember.VStack(
    ember.Box(ember.TextField(
        ember.Text("The quick brown fox jumped over the lazy dog.", align="center",
                   style=big_text, color=(255, 255, 255), width=ember.FILL),
        size=(ember.FILL, ember.FILL)),
             size=(500, 200), resizable_side=["left", "right"], resize_limits=(300, 800)),

    ember.Slider(size=(500, 100)),
    frame_counter,
    spacing=30,
    size=(ember.FILL, ember.FILL))
view = ember.View(
    ember.HStack(content)
)

while True:
    for event in pygame.event.get():
        view.event(event)

        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit(0)

    screen.blit(wallpaper, (0, 0))
    frame_counter.set_text(f"FPS: {(round(clock.get_fps()))}")
    ember.update()
    view.update(screen)

    clock.tick(60)
    pygame.display.flip()
