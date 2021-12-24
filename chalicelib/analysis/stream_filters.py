import abc
from typing import Iterable

from chalicelib.services import eod_historical_data


class StreamFilter(abc.ABC):
    @abc.abstractmethod
    def is_valid(self, entry: eod_historical_data.EodDataEntry) -> bool:
        pass


class AfterDateFilter(StreamFilter):
    def __init__(self, from_: "datetime.datetime"):
        self.from_ = from_

    def is_valid(self, entry: eod_historical_data.EodDataEntry) -> bool:
        return self.from_ <= entry.date


class RangeFilter(StreamFilter):
    def __init__(self, from_: "datetime.datetime", to: "datetime.datetime"):
        self.from_ = from_
        self.to = to

    def is_valid(self, entry: eod_historical_data.EodDataEntry) -> bool:
        return self.from_ <= entry.date <= self.to


class HasValueFilter(StreamFilter):
    def __init__(self, field_name):
        self.field_name = field_name

    def is_valid(self, entry: eod_historical_data.EodDataEntry) -> bool:
        return entry.get(self.field_name)


class AverageDailyVolumeFilter(StreamFilter):
    def __init__(self, minimum_volume: int):
        self.min_volume = minimum_volume

    def is_valid(self, entry: eod_historical_data.EodDataEntry) -> bool:
        return entry.volume > self.min_volume


def apply_filters(data, filters: Iterable[StreamFilter]):
    stream = data
    for filtr in filters:
        stream = filter(filtr.is_valid, stream)
    return stream
