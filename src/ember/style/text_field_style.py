import pygame
from typing import Union, Optional, Sequence
try:
    from typing import Literal
except ModuleNotFoundError:
    from typing_extensions import Literal


from .. import common as _c
from .style import Style, MaterialType

from .load_material import load_material
from ..transition.transition import Transition

from ..size import SizeType, FILL

from ..material.material import Material


class TextFieldStyle(Style):
    def __init__(self,
                 default_size: Sequence[SizeType] = (300, 80),
                 default_scroll_size: Sequence[SizeType] = (FILL, FILL),

                 material: MaterialType = None,
                 hover_material: MaterialType = None,
                 active_material: MaterialType = None,
                 disabled_material: MaterialType = None,

                 cursor_blink_speed: float = 0.5,
                 text_align: Literal["left", "centre", "right"] = "centre",
                 text_fade: Union[pygame.Surface, str, None] = None,
                 fade_width: Optional[int] = None,
                 text_color: Union[str, tuple[int,int,int], pygame.Color, None] = None,

                 prompt_color: Union[str, tuple[int,int,int], pygame.Color, None] = None,
                 highlight_color: Union[str, tuple[int,int,int], pygame.Color] = (100,100,150),
                 cursor_color: Union[str, tuple[int,int,int], pygame.Color] = (255, 255, 255),

                 key_repeat_delay: float = 0.1,
                 key_repeat_start_delay: float = 0.5,

                 material_transition: Optional[Transition] = None):

        self.default_size: Sequence[SizeType] = default_size
        self.default_scroll_size: Sequence[SizeType] = default_scroll_size

        self._material: Material = load_material(material, None)
        self._hover_material: Material = load_material(hover_material, material)
        self._active_material: Material = load_material(active_material, hover_material)
        self._disabled_material: Material = load_material(disabled_material, material)

        self.cursor_blink_speed: float = cursor_blink_speed
        self.text_align: Literal["left", "centre", "right"] = text_align
        self.text_color = text_color

        self.prompt_color = prompt_color if prompt_color is not None else text_color
        self.highlight_color = highlight_color
        self.cursor_color = cursor_color

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

        self.key_repeat_delay = key_repeat_delay
        self.key_repeat_start_delay = key_repeat_start_delay

        self.material_transition = material_transition

    def set_as_default(self) -> "TextFieldStyle":
        _c.default_text_field_style = self
        return self

    material = property(
        fget=lambda self: self._material,
        fset=lambda self, value: setattr(self, "_material", load_material(value, None))
    )

    hover_material = property(
        fget=lambda self: self._hover_material,
        fset=lambda self, value: setattr(self, "_hover_material", load_material(value, None))
    )

    active_material = property(
        fget=lambda self: self._active_material,
        fset=lambda self, value: setattr(self, "_active_material", load_material(value, None))
    )

    disabled_material = property(
        fget=lambda self: self._disabled_material,
        fset=lambda self, value: setattr(self, "_disabled_material", load_material(value, None))
    )
