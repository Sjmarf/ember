from ember.ui.icon import Icon as _Icon
from ember.font.icon_font import IconFont
from ember.material.color import Color

from ember.common import package
from ember._init import init_task

class Icon(_Icon):
    pass

@init_task
def _():
    Icon.font.default_value = IconFont(
        path=package.joinpath(f"default_icon_fonts/pixel")
    )
    Icon.primary_material.default_value = Color("white")

del _