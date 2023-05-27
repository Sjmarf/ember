import logging
from typing import Union


class Indentor:
    def __init__(self, logger: Union["CustomLogger", "MaterialLogger"]):
        self.logger = logger

    def __enter__(self) -> "Indentor":
        self.logger.indent_string += "    "
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.logger.indent_string = self.logger.indent_string[:-4]


class CustomLogger:
    def __init__(self, name: str):
        self.indent = Indentor(self)
        self.logger = logging.getLogger(name)
        self.indent_string = ""

    def debug(self, obj, msg):
        self.logger.debug(f"{self.indent_string}{obj}: {msg}")

    def info(self, obj, msg):
        self.logger.info(f"{self.indent_string}{obj}: {msg}")

    def line_break(self, text="", lines=1):
        self.logger.info(text + "\n" * (lines - 1))


class MaterialLogger:
    def __init__(self, name: str):
        self.indent = Indentor(self)
        self.logger = logging.getLogger(name)
        self.indent_string = ""

    def debug(self, obj, element, msg):
        self.logger.debug(f"{self.indent_string}{element} {obj}: {msg}")

    def info(self, obj, element, msg):
        self.logger.info(f"{self.indent_string}{element} {obj}: {msg}")

    def line_break(self, text="", lines=1):
        self.logger.info(text + "\n" * (lines - 1))


nav = CustomLogger("ember.nav")
material = MaterialLogger("ember.material")
size = CustomLogger("ember.size")
layer = CustomLogger("ember.layer")
