import pygame
from ember import common as _c

class ScaledSurface(pygame.Surface):
    def __init__(self, parent_surface, scale_factor, *args, **kwargs):
        self.parent_surface = parent_surface
        self.scale_factor = scale_factor
        size = parent_surface.get_size()
        super().__init__((size[0]/scale_factor,size[1]/scale_factor), pygame.SRCALPHA, *args, *kwargs)
        _c.mouse_pos = [0,0]
        
    def resize(self):
        size = self.parent_surface.get_size()
        super().__init__((size[0]/self.scale_factor,size[1]/self.scale_factor), pygame.SRCALPHA)
        
    def draw_to_screen(self):
        self.parent_surface.blit(pygame.transform.scale(self, self.parent_surface.get_size()), (0,0))
        _c.mouse_pos = [i//self.scale_factor for i in pygame.mouse.get_pos()]
