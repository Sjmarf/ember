from typing import Union, TYPE_CHECKING
from .position import Position
from .absolute_position import AbsolutePosition

if TYPE_CHECKING:
    from ember.trait.trait import Trait

def load_position(pos: Union["Position", float, "Trait", None]) -> Union["Position", "Trait", None]:
    return AbsolutePosition(pos) if isinstance(pos, (int, float)) else pos
