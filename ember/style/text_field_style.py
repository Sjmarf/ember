import pygame
from typing import Union, Literal, Optional

from ember import common as _c
from ember.style.style import Style, MaterialType

from ember.material.material import Material
from ember.style.load_material import load_material
from ember.transition.transition import Transition


class TextFieldStyle(Style):
    def __init__(self,
                 default_image: MaterialType = None,
                 hover_image: MaterialType = None,
                 active_image: MaterialType = None,
                 disabled_image: MaterialType = None,

                 cursor_blink_speed: float = 0.5,
                 text_align: Literal["left", "centre"] = "centre",
                 text_fade: Union[pygame.Surface, str, None] = None,
                 fade_width: Optional[int] = None,
                 text_color: Union[str, tuple[int,int,int], pygame.Color, None] = None,

                 prompt_color: Union[str, tuple[int,int,int], pygame.Color, None] = None,
                 highlight_color: Union[str, tuple[int,int,int], pygame.Color] = (100,100,150),
                 cursor_color: Union[str, tuple[int,int,int], pygame.Color] = (255, 255, 255),

                 backspace_repeat_speed: float = 0.1,
                 backspace_start_delay: float = 0.5,
                 padding: int = 10,

                 material_transition: Optional[Transition] = None):

        default_image = load_material(default_image, None)
        hover_image = load_material(hover_image, default_image)
        self.images = [default_image,
                       hover_image,
                       load_material(active_image, hover_image),
                       load_material(disabled_image, default_image)]

        self.cursor_blink_speed = cursor_blink_speed
        self.text_color = text_color
        self.prompt_color = prompt_color if prompt_color is not None else text_color
        self.highlight_color = highlight_color
        self.cursor_color = cursor_color

        self.padding = padding

        self.text_align = text_align
        if text_fade:
            text_fade = pygame.image.load(text_fade).convert_alpha() if type(text_fade) is str else text_fade
            self.text_fade = pygame.transform.scale(text_fade,
                                                    (text_fade.get_width(), 100))
        elif fade_width:
            path = _c.package.joinpath(f'fonts/text_fade.png')
            self.text_fade = pygame.transform.scale(pygame.image.load(path),
                                                    (fade_width, 100))

        else:
            self.text_fade = pygame.Surface((1,1),pygame.SRCALPHA)

        self.backspace_repeat_speed = backspace_repeat_speed
        self.backspace_start_delay = backspace_start_delay

        self.material_transition = material_transition

    def set_as_default(self):
        _c.default_text_field_style = self
