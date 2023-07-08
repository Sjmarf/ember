import math

class TextVariant:
    def __init__(self, _id: int = math.inf):
        self._id = _id

    def __gt__(self, other: "TextVariant"):
        if isinstance(other, TextVariant):
            return self._id > other._id
        return NotImplemented

    def __lt__(self, other: "TextVariant"):
        if isinstance(other, TextVariant):
            return self._id < other._id
        return NotImplemented


BOLD = TextVariant(0)
ITALIC = TextVariant(1)
STRIKETHROUGH = TextVariant(2)
UNDERLINE = TextVariant(3)
OUTLINE = TextVariant(4)
