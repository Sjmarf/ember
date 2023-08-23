from .spacing import Spacing


class InterpolatedSpacing(Spacing):
    def __init__(self, old_spacing: Spacing, new_spacing: Spacing) -> None:
        self.old_spacing: Spacing = old_spacing
        self.new_spacing: Spacing = new_spacing
        self.progress: float = 0

    def __repr__(self) -> str:
        return f"<InterpolatedSpacing({self.old_spacing} -> {self.new_spacing}: {self.progress * 100: .0f}%)>"

    def get(self, available_size: int = 0) -> float:
        old_val = self.old_spacing.get(available_size)
        new_val = self.new_spacing.get(available_size)
        return round(old_val + (new_val - old_val) * self.progress)

    def get_min(self) -> int:
        old_val = self.old_spacing.get_min()
        new_val = self.new_spacing.get_min()
        return round(old_val + (new_val - old_val) * self.progress)
