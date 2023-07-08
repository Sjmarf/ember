import logging
from typing import Union, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .ui.base.element import Element
    from .material.material import Material

class Indentor:
    def __init__(self, logger: Union["CustomLogger", "MaterialLogger"]):
        self.logger = logger

    def __enter__(self) -> "Indentor":
        self.logger.indent_string += "    "
        return self

    def __exit__(self, type_, value, traceback) -> None:
        self.logger.indent_string = self.logger.indent_string[:-4]


class CustomLogger:
    def __init__(self, name: str) -> None:
        self.indent = Indentor(self)
        self.logger = logging.getLogger(name)
        self.indent_string = ""

    def debug(self, obj: Any, msg: str) -> None:
        self.logger.debug(f"{self.indent_string}{obj}: {msg}")

    def info(self, obj: Any, msg: str) -> None:
        self.logger.info(f"{self.indent_string}{obj}: {msg}")

    def line_break(self, text: str = "", lines: int = 1) -> None:
        self.logger.info(text + "\n" * (lines - 1))
        

class MaterialLogger:
    def __init__(self, name: str) -> None:
        self.indent = Indentor(self)
        self.logger = logging.getLogger(name)
        self.indent_string = ""

    def debug(self, material: "Material", element: "Element", msg: str) -> None:
        self.logger.debug(f"{self.indent_string}{element} {material}: {msg}")

    def info(self, material: "Material", element: "Element", msg: str) -> None:
        self.logger.info(f"{self.indent_string}{element} {material}: {msg}")

    def line_break(self, text: str = "", lines: int = 1) -> None:
        self.logger.info(text + "\n" * (lines - 1))


nav = CustomLogger("ember.nav")
material = MaterialLogger("ember.material")
font = CustomLogger("ember.font")
size = CustomLogger("ember.size")
layer = CustomLogger("ember.layer")
# Multi-layer Surfacable
mls = CustomLogger("ember.mls")
