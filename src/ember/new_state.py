from typing import TypeVar, Generic, TYPE_CHECKING, Optional

from . import common as _c
from . import log

if TYPE_CHECKING:
    from .ui.base.element import Element

class State:
    def __init__(self):
        self.call_list: list[tuple[int, callable]] = []
    
    def activate_on(self, event_type: int) -> callable:
        def decorator(func: callable) -> callable:
            self.call_list.append((event_type, func))
            return func
        return decorator