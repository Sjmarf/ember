from typing import Union, TYPE_CHECKING

from .size import Size
from .absolute_size import AbsoluteSize

if TYPE_CHECKING:
    from ember.trait.trait import Trait
def load_size(value: Union["Size", float, "Trait", None]) -> Union["Size", "Trait", None]:
    if isinstance(value, (float, int)):
        return AbsoluteSize(value)
    return value
