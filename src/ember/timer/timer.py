import abc


class Timer(abc.ABC):
    @abc.abstractmethod
    def get(self, value: float) -> float:
        pass

    def interpolate(self, first, second, value: float) -> float:
        return first + (second - first) * self.get(value)
