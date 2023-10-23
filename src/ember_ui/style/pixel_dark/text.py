from ember_ui.ui.text import Text as _Text
from ember_ui.font.pixel_font import PixelFont
from ember_ui.material.color import Color

from ember_ui.common import package
from ember_ui._init import init_task

class Text(_Text):
    pass

@init_task
def _():
    Text.font.default_value = PixelFont(
        path=package.joinpath(f"default_fonts/pixel")
    )
    Text.primary_material.default_value = Color("white")
    
del _