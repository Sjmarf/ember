class Line:
    def __init__(
        self,
        content: str = "",
        start_x: int = 0,
        start_y: int = 0,
        width: int = 0,
        start_index: int = 0,
        line_index: int = 0,
    ):
        self.content = content
        self.start_index = start_index
        self.end_index = self.start_index + len(self.content) - 1
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.line_index = line_index

    def __repr__(self) -> str:
        content = self.content if len(self.content) <= 15 else f"{self.content[:16]}"
        return f"<Line('{content}', start_index={self.start_index})>"

    def __len__(self) -> int:
        return len(self.content)
