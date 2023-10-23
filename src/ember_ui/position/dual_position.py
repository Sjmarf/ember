from .position import Position


class DualPosition:
    def __init__(self, x: Position, y: Position):
        self.x = x
        self.y = y


class XYDualPosition(DualPosition):
    def __add__(self, other):
        self.x += other
        self.y += other
        return self

    def __sub__(self, other):
        self.x -= other
        self.y -= other
        return self

    def __mul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __truediv__(self, other):
        self.x /= other
        self.y /= other
        return self


class XDualPosition(DualPosition):
    def __add__(self, other):
        self.x += other
        return self

    def __sub__(self, other):
        self.x -= other
        return self

    def __mul__(self, other):
        self.x *= other
        return self

    def __truediv__(self, other):
        self.x /= other
        return self


class YDualPosition(DualPosition):
    def __add__(self, other):
        self.y += other
        return self

    def __sub__(self, other):
        self.y -= other
        return self

    def __mul__(self, other):
        self.y *= other
        return self

    def __truediv__(self, other):
        self.y /= other
        return self


class TopLeftPosition(XYDualPosition):
    pass


class TopRightPosition(XYDualPosition):
    pass


class BottomLeftPosition(XYDualPosition):
    pass


class BottomRightPosition(XYDualPosition):
    pass


class MidLeftPosition(XDualPosition):
    pass


class MidRightPosition(XDualPosition):
    pass


class MidTopPosition(YDualPosition):
    pass


class MidBottomPosition(YDualPosition):
    pass
