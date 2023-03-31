from ember import common as _c
from typing import Optional


class BasicTimer:
    def __init__(self, value: float):
        self.val = value
        self.stop_at = 0
        self.direction = 1
        self.speed = 1
        self.playing = False

    def tick(self):
        if self.playing:
            self.val += self.direction * _c.delta_time * self.speed
            if self.direction == 1:
                if self.val >= self.stop_at:
                    self.playing = False
                    self.val = self.stop_at
            else:
                if self.val <= self.stop_at:
                    self.playing = False
                    self.val = self.stop_at

    def play(self, stop: float, duration: float = 1, speed: Optional[float] = None):
        self.playing = True
        self.stop_at = stop
        self.direction = -1 if self.val > stop else 1
        self.speed = abs(self.stop_at - self.val) / duration if speed is None else speed
