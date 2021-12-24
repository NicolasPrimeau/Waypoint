import json
import logging
from typing import List, Iterable

from chalicelib import models
from chalicelib.config import CONFIG
from chalicelib.data import tickers
from chalicelib.services import eod_historical_data, s3, sns

_logger = logging.getLogger()


class EodDataFile(dict):
    @classmethod
    def new(cls, ticker: models.Ticker):
        return cls({"ticker": str(ticker), "data": list()})

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])

    @property
    def data(self) -> List[eod_historical_data.EodDataEntry]:
        return list(self.get("data"))

    @data.setter
    def data(self, values: List[eod_historical_data.EodDataEntry]):
        self["data"] = list(values)


class EodUpdateSNSEvent(models.SNSEvent):
    def new(self, ticker: models.Ticker):
        self["ticker"] = str(ticker)

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])


def update_all_to_etf_prices(from_, to):
    for ticker in tickers.iterate_toronto_etfs():
        _logger.info(f"Updating {str(ticker)}")
        update_to_etf_price(ticker, from_, to)
        sns.publish(CONFIG.SNS_EOD_DATA_UPDATE_TOPIC_ARN, EodUpdateSNSEvent.new(ticker))


def update_to_etf_price(ticker: models.Ticker, from_, to):
    s3_key = f"{CONFIG.S3_TICKET_INFO_FOLDER_KEY}/{str(ticker)}"
    raw_data = s3.get_file_data(CONFIG.S3_BUCKET, s3_key)
    if raw_data:
        existing_data = EodDataFile(json.loads(raw_data))
    else:
        existing_data = EodDataFile.new(ticker)

    eod_data = list(eod_historical_data.get_eod_data(ticker, from_=from_, to=to))
    combined_data = _combine_data(existing_data, eod_data)
    s3.put_file_data(CONFIG.S3_BUCKET, s3_key, json.dumps(combined_data))


def _combine_data(
        existing_data: EodDataFile, new_data: List[eod_historical_data.EodDataEntry]
) -> Iterable[eod_historical_data.EodDataEntry]:
    data = existing_data.data
    dates = set(entry.date for entry in data)

    for entry in new_data:
        if entry.date not in dates:
            data.append(entry)
            dates.add(entry.date)

    return list(sorted(data, key=lambda e: e.date))
