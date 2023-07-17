from typing import TypeVar, Generic, TYPE_CHECKING, Optional

from . import common as _c
from . import log

if TYPE_CHECKING:
    from .ui.base.element import Element

T = TypeVar("T")

class Trait(Generic[T]):
    
    inspected_layer = -1
    __slots__ = ("layers", "element", "value", "chain_up")
    
    def __init__(self, *items: Optional[T], element: "Element", n: int = 1, chain_up: bool = False) -> None:
        
        self.element: "Element" = element
        self.chain_up: bool = chain_up
        self.value: Optional[T] = None
        
        self.layers: list[Optional[T]]
        # Layers with lower index have higher priority 
        
        if items:
            self.layers = items
            self.update()
        else:
            
            self.layers = [None]*n
    
    def __getitem__(self, key: int) -> T:
        return self.layers[key]
    
    def __setitem__(self, key: int, value: T) -> None:
        if self.layers[key] is not value:
            self.layers[key] = value
            self.update()
    
    def set_value(self, value: Optional[T], n: Optional[int] = None) -> None:
        if n is None:
            n = self.inspected_layer
            
        if self.layers[inspected_layer] is not value:
            self.layers[inspected_layer] = value
            self.update()
            
    def update(self) -> None:
        for i in self.layers:
            if i is not None:
                if i is not self.value:
                    self.value = i
                    if chain_up:
                        log.size.line_break()
                        log.size.info(self.element, "Trait modified, starting chain up...")
                        with log.size.indent:
                            element._update_rect_chain_up()
                return
        raise _c.Error("No value found in Trait")