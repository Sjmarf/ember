from .trait import Trait


from ..position import Position, PositionType, load_position


class PositionTrait(Trait[Position]):
    @staticmethod
    def load_value(value: PositionType) -> Position:
        return load_position(value)
