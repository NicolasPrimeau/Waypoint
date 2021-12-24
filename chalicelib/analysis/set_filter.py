import abc
from typing import Iterable

from chalicelib.services import eod_historical_data


class SetFilter(abc.ABC):
    @abc.abstractmethod
    def is_valid(self, data: Iterable[eod_historical_data.EodDataEntry]) -> bool:
        pass


class IsAverageVolumeAboveMinimumFilter(SetFilter):
    def __init__(self, min_volume: float):
        self.min_volume = min_volume

    def is_valid(self, data: Iterable[eod_historical_data.EodDataEntry]) -> bool:
        data = list(data)
        if not data:
            return False

        return (sum(map(lambda e: e.volume, data)) / len(data)) > self.min_volume


class MaxMinSpreadMinimumFilter(SetFilter):
    def __init__(self, min_spread: float):
        self.min_spread = min_spread

    def is_valid(self, data: Iterable[eod_historical_data.EodDataEntry]) -> bool:
        data = list(data)
        if not data:
            return False

        max_val = max(map(lambda e: e.close, data))
        min_val = min(map(lambda e: e.close, data))

        return (max_val - min_val) > self.min_spread
