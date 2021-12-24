import json
import logging
from typing import List, Iterable, Optional

from chalicelib import models, events
from chalicelib.config import CONFIG
from chalicelib.data import tickers
from chalicelib.services import eod_historical_data, s3, sns, sqs

_logger = logging.getLogger()


class EodDataFile(dict):
    @classmethod
    def new(cls, ticker: models.Ticker):
        return cls({"ticker": str(ticker), "data": []})

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])

    @property
    def data(self) -> List[eod_historical_data.EodDataEntry]:
        return list(map(eod_historical_data.EodDataEntry, self.get("data")))

    @data.setter
    def data(self, values: List[eod_historical_data.EodDataEntry]):
        self["data"] = list(values)


def trigger_refresh_event_requests(from_, to):
    for ticker in tickers.iterate_toronto_etfs():
        sqs.publish(CONFIG.SQS_EOD_DATA_UPDATE_QUEUE_URL, events.EodDataRefreshSQSEvent.new(ticker, from_, to))


def handle_refresh_event_request(event: events.EodDataRefreshSQSEvent):
    update_to_etf_eod_price(event.ticker, event.from_, event.to)


def _get_eod_file_key(ticker: models.Ticker) -> str:
    return f"{CONFIG.S3_TICKET_INFO_FOLDER_KEY}/{str(ticker).upper()}"


def get_eod_price_file(ticker: models.Ticker) -> Optional[EodDataFile]:
    raw_data = s3.get_file_data(CONFIG.S3_BUCKET, _get_eod_file_key(ticker))
    return EodDataFile(json.loads(raw_data)) if raw_data else None


def put_eod_price_file(document: EodDataFile):
    s3.put_file_data(CONFIG.S3_BUCKET, _get_eod_file_key(document.ticker), json.dumps(document))


def update_to_etf_eod_price(ticker: models.Ticker, from_, to):
    document = get_eod_price_file(ticker)
    if not document:
        document = EodDataFile.new(ticker)

    eod_data = list(eod_historical_data.get_eod_data(ticker, from_=from_, to=to))
    document.data = _combine_data(document.data, eod_data)
    put_eod_price_file(document)
    sns.publish(CONFIG.SNS_EOD_DATA_UPDATE_TOPIC_ARN, events.EodUpdateSNSEvent.new(ticker))


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
