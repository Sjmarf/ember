import pygame
from typing import Callable

from . import common as _c

init_queue: list[Callable[[], None]] = []
has_init: bool = False

def init():
    if not pygame.get_init():
        raise _c.Error("You must call pygame.init() before ember.init()")
    
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
