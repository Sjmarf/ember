from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ember.ui.container import Container

from .trait import Trait
from .bound_trait import BoundTrait
from .bound_trait import TraitReference
from .cascading_trait_value import CascadingTraitValue

from ember import log

class CascadeRepository:
    __slots__ = ("element", "values")
    
    def __init__(self, element: "Container", values: Sequence[CascadingTraitValue]) -> None:
        self.element: "Container" = element
        self.values: list[CascadingTraitValue] = []
        for i in values:
            self.add(i)
            
    def __iter__(self):
        return iter(self.values)
    
    def __contains__(self, ref: TraitReference) -> bool:
        return any(i.ref == ref for i in self.values)
        
    def __getitem__(self, key: BoundTrait) -> CascadingTraitValue:
        ref = key.create_reference()
        for value in self.values:
            if value.ref == ref:
                return value
        return CascadingTraitValue(ref=ref, value=key.default_value, depth=key.trait.default_cascade_depth)
    
    def __setitem__(self, key: BoundTrait, value: CascadingTraitValue) -> None:
        ref = key.create_reference()
        if key.trait is not value.ref.trait:
            raise ValueError("CascadingTraitValue doesn't match key")
        
        for n,i in enumerate(self.values):
            if i.ref == ref:
                del self.values[n]
                break
            
        self.values.append(value)
        self.element.start_cascade(value)
        
    def __delitem__(self, key: BoundTrait) -> None:
        ref = key.create_reference()
        for n,value in enumerate(self.values):
            if value.ref == ref:
                del self.values[n]
                self.element.start_cascade(
                    CascadingTraitValue(
                        trait=value.trait,
                        value=None,
                        depth=value.depth
                    )
                )
               
    def add(self, value: CascadingTraitValue) -> None:
        with log.cascade.indent(f"Value added to {self.element}..."):
            self.values.append(value)
            self.element.start_cascade(value)