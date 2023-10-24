import logging
from typing import TYPE_CHECKING, Any, Generator, Optional
from contextlib import contextmanager

if TYPE_CHECKING:
    from .material.material import Material


class CustomLogger:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        self.indent_string = ""

    @contextmanager
    def indent(self, msg="", obj: Any = None) -> Generator[None, None, None]:
        if msg:
            self.info(msg, obj)
        self.indent_string += "    "
        yield
        self.indent_string = self.indent_string[:-4]

    def info(self, msg: str, obj: Any = None) -> None:
        if obj is None:
            self.logger.info(f"{self.indent_string}{msg}")
        else:
            self.logger.info(f"{self.indent_string}{obj}: {msg}")

    def line_break(self, text: str = "", lines: int = 1) -> None:
        self.logger.info(text + "\n" * (lines - 1))


class MaterialLogger(CustomLogger):
    def info(
        self, msg: str, obj: Any = None, material: Optional["Material"] = None
    ) -> None:
        if obj is None:
            self.logger.info(f"{self.indent_string}{msg}")
        elif material is None:
            self.logger.info(f"{self.indent_string}{obj}: {msg}")
        else:
            self.logger.info(f"{self.indent_string}{obj} {material}: {msg}")


nav = CustomLogger("ember.nav")
material = MaterialLogger("ember.material")
font = CustomLogger("ember.font")
size = CustomLogger("ember.size")
ancestry = CustomLogger("ember.ancestry")
style = CustomLogger("ember.style")
trait = CustomLogger("ember.trait")
cascade = CustomLogger("ember.cascade")
event_listener = CustomLogger("ember.event_listener")
# Multi-layer Surfacable
mls = CustomLogger("ember.mls")
