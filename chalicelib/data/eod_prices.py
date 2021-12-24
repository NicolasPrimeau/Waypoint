import datetime
import json
import logging
from typing import List, Iterable

from chalicelib import models
from chalicelib.config import CONFIG
from chalicelib.data import tickers
from chalicelib.services import eod_historical_data, s3, sns, sqs

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
        return list(map(eod_historical_data.EodDataEntry, self.get("data")))

    @data.setter
    def data(self, values: List[eod_historical_data.EodDataEntry]):
        self["data"] = list(values)


class EodUpdateSNSEvent(sns.SNSEvent):
    @classmethod
    def new(cls, ticker: models.Ticker):
        return cls({"ticker": str(ticker)})

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])


class EodDataRefreshSQSEvent(sqs.SQSEvent):
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


def trigger_refresh_event_requests(from_, to):
    for ticker in tickers.iterate_toronto_etfs():
        sqs.publish(CONFIG.SQS_EOD_DATA_UPDATE_QUEUE_URL, EodDataRefreshSQSEvent.new(ticker, from_, to))


def handle_refresh_event_request(event: EodDataRefreshSQSEvent):
    update_to_etf_eod_price(event.ticker, event.from_, event.to)


def update_to_etf_eod_price(ticker: models.Ticker, from_, to):
    s3_key = f"{CONFIG.S3_TICKET_INFO_FOLDER_KEY}/{str(ticker)}"
    raw_data = s3.get_file_data(CONFIG.S3_BUCKET, s3_key)
    if raw_data:
        document = EodDataFile(json.loads(raw_data))
    else:
        document = EodDataFile.new(ticker)

    eod_data = list(eod_historical_data.get_eod_data(ticker, from_=from_, to=to))
    document.data = _combine_data(document.data, eod_data)
    s3.put_file_data(CONFIG.S3_BUCKET, s3_key, json.dumps(document))
    sns.publish(CONFIG.SNS_EOD_DATA_UPDATE_TOPIC_ARN, EodUpdateSNSEvent.new(ticker))


def _combine_data(
        existing_data: List[eod_historical_data.EodDataEntry], new_data: List[eod_historical_data.EodDataEntry]
) -> Iterable[eod_historical_data.EodDataEntry]:
    data = list(existing_data)
    dates = set(entry.date for entry in data)

    for entry in new_data:
        if entry.date not in dates:
            data.append(entry)
            dates.add(entry.date)

    return list(sorted(data, key=lambda e: e.date))
