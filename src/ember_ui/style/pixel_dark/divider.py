from ember.ui.divider import Divider as _Divider
from ember.material.color import Color

from ember.common import package
from ember._init import init_task
from ember.size import FILL, PivotableSize

root = package / "style/pixel_dark/assets/divider"

class Divider(_Divider):
    ...

@init_task
def _():
    Divider.material.default_value = Color((0, 0, 0, 100)) #StretchedSurface(root/"divider.png", edge=(1,1,1,1))
    size = PivotableSize(FILL - 4, 1)
    Divider.w.default_value = size
    Divider.h.default_value = PivotableSize(1, FILL - 4)
