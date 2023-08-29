from .trait import Trait


from ..spacing import Spacing, SpacingType, load_spacing


class SpacingTrait(Trait[Spacing]):
    @staticmethod
    def load_value(value: SpacingType) -> Spacing:
        return load_spacing(value)
