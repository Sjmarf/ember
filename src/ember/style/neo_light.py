from functools import cached_property

import pygame.font

from .. import ui
from .. import font
from .. import material
from ..common import package


class NeoLight:
    background_color = (236, 240, 243)
    @cached_property
    def Text(self):

        class NeoLightText(ui.Text):
            pass

        NeoLightText.font_.default_value = font.PygameFont(pygame.font.SysFont("SF Compact Rounded", 40))
        return NeoLightText
