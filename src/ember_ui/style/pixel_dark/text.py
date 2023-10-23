from ember.ui.text import Text as _Text
from ember.font.pixel_font import PixelFont
from ember.material.color import Color

from ember.common import package
from ember._init import init_task

class Text(_Text):
    pass

@init_task
def _():
    Text.font.default_value = PixelFont(
        path=package.joinpath(f"default_fonts/pixel")
    )
    Text.primary_material.default_value = Color("white")
    
del _