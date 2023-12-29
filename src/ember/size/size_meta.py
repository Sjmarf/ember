from abc import ABCMeta, ABC
from typing import TYPE_CHECKING
import inspect

if TYPE_CHECKING:
    from .size import Size
    

class SizeMeta(ABCMeta):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if ABC not in bases:
            cls.calculate_class_intents()
        
    def calculate_class_intents(cls: "Size") -> None:
        if (func := getattr(cls, "_get", None)) is not None:
            cls.min_value_intent = False
            cls.max_value_intent = False
            cls.other_value_intent = False
            cls.resizable_value_intent = False
            cls.axis_intent = False
            
            for param in inspect.signature(func).parameters.values():
                if param.kind in {param.VAR_POSITIONAL, param.VAR_KEYWORD}:
                    cls.min_value_intent = True
                    cls.max_value_intent = True
                    cls.other_value_intent = True
                    cls.resizable_value_intent = True
                    cls.axis_intent = True
                    return
                
                if param.name == "min_value":
                    cls.min_value_intent = True
                elif param.name == "max_value":
                    cls.max_value_intent = True
                elif param.name == "other_value":
                    cls.other_value_intent = True
                elif param.name == "resizable_value":
                    cls.resizable_value_intent = True
                elif param.name == "axis":
                    cls.axis_intent = True

        else:
            raise AttributeError("Class does not implement _get method.")
    
