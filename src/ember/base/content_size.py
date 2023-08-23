from typing import Optional, Sequence
from ember.size import SizeType, Size, OptionalSequenceSizeType, load_size

from ember.base.element import Element
from ember.trait import new_trait


class ContentW(Element):
    content_w, content_w_ = new_trait(None)

    print("ContentW")
    def __init__(self, *args, content_w: Optional[SizeType] = None, **kwargs):
        self.content_w = load_size(content_w)
        super().__init__(*args, **kwargs)


class ContentH(Element):
    content_h, content_h_ = new_trait(None)

    def __init__(self, *args, content_h: Optional[SizeType] = None, **kwargs):
        self.content_h = load_size(content_h)
        super().__init__(*args, **kwargs)


class ContentSize(ContentW, ContentH):
    def __init__(
        self,
        *args,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        **kwargs,
    ):
        if not isinstance(content_size, Sequence):
            content_size = content_size, content_size

        content_w = content_w if content_w is not None else content_size[0]
        content_h = content_h if content_h is not None else content_size[1]

        super().__init__(*args, content_w=content_w, content_h=content_h, **kwargs)

    @property
    def content_size(self) -> tuple[Optional[Size], Optional[Size]]:
        return self.content_w, self.content_h

    @content_size.setter
    def content_size(self, value: OptionalSequenceSizeType) -> None:
        if not isinstance(value, Sequence):
            value = value, value

        self.content_w = value[0]
        self.content_h = value[1]
