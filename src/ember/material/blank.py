from .material import Material

class Blank(Material):
    def __init__(self):
        super().__init__()

    def render(self, element, surface, pos, size, alpha):
        pass
