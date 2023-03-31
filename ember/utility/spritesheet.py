from pygame import image, Surface, SRCALPHA, error


class SpriteSheet:
    def __init__(self, img: Surface) -> None:
        if type(img) == str:
            self.img = image.load(img).convert_alpha()
        elif type(img) == Surface:
            self.img = img
        else:
            raise TypeError("'filename' must be of type pygame.Surface or str")

    def image(self, x: int, y: int, w: int, h: int) -> Surface:
        try:
            surf = Surface((w, h), SRCALPHA)
        except error:
            raise ValueError(f'requested SpriteSheet image size ({x},{y},{w},{h}) is out of bounds.')
        surf.blit(self.img, (x * -1, y * -1))
        return surf
