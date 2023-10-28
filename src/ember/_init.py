import pygame
from typing import Callable

from . import common as _c

init_queue: list[Callable[[], None]] = []
has_init: bool = False

def init():
    if not (pygame.get_init() and pygame.display.get_active()):
        raise _c.Error("You must call pygame.init() and pygame.display.set_mode() before ember.init()")
    
    for i in init_queue:
        i()
        
    init_queue.clear()
    has_init = True
    
def init_task(func: Callable[[], None]) -> Callable[[], None]:
    if has_init:
        func()
    else:
        init_queue.append(func)
    return func
