import datetime
from typing import Dict

from chalicelib import models
from chalicelib.services import eod_historical_data


class SQSEvent(dict):
    pass


class SNSEvent(dict):
    pass


class EodUpdateSNSEvent(SNSEvent):
    @classmethod
    def new(cls, ticker: models.Ticker):
        return cls({"ticker": str(ticker)})

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])


class EodDataRefreshSQSEvent(SQSEvent):
    @classmethod
    def new(cls, ticker: models.Ticker, from_, to):
        return cls({
            "ticker": str(ticker),
            "from": from_.strftime(eod_historical_data.DATE_FORMAT),
            "to": to.strftime(eod_historical_data.DATE_FORMAT)
        })

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])

    @property
    def from_(self):
        return datetime.datetime.strptime(self["from"], eod_historical_data.DATE_FORMAT)

    @property
    def to(self):
        return datetime.datetime.strptime(self["to"], eod_historical_data.DATE_FORMAT)


class TradeSignalEvent(SNSEvent):
    @classmethod
    def new(cls, ticker: models.Ticker, predicted_change: float, source: str):
        return cls({
            "ticker": str(ticker),
            "predicted_change": predicted_change,
            "source": source,
            "creation_datetime": datetime.datetime.utcnow().isoformat()
        })

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])

    @property
    def predicted_change(self) -> float:
        return self["predicted_change"]

    @property
    def source(self) -> str:
        return self["source"]

    @property
    def creation_datetime(self) -> "datetime.datetime":
        return datetime.datetime.fromisoformat(self["creation_datetime"])


class TradeSignalsEmailEvent(SNSEvent):
    @classmethod
    def new(cls):
        return cls({
            "signals": {},
        })

    @property
    def signals(self) -> Dict:
        return self["signals"]
