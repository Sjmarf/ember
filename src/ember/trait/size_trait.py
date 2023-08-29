from .trait import Trait


from ..size import load_size, SizeType, Size


class SizeTrait(Trait[Size]):
    @staticmethod
    def load_value(value: SizeType) -> Size:
        return load_size(value)
