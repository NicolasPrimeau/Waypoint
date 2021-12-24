import abc

from chalicelib.data import eod_prices


class Detector(abc.ABC):
    @abc.abstractmethod
    def detect(self, document: eod_prices.EodDataFile) -> float:
        pass
