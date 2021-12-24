import logging
from typing import Tuple, Iterable, List
import datetime

from chalicelib import events, models
from chalicelib.analysis import detectors, stream_filters, set_filter
from chalicelib.config import CONFIG
from chalicelib.data import eod_prices
from chalicelib.services import eod_historical_data, sns

_logger = logging.getLogger()


MIN_SPREAD = 2
MIN_AVERAGE_VOLUME = 20000
MIN_PERCENTAGE = 0.05

FIRST_PERIOD_START_DELTA = datetime.timedelta(weeks=26)
FIRST_PERIOD_END_DELTA = datetime.timedelta(weeks=4)

SECOND_PERIOD_START_DELTA = datetime.timedelta(weeks=2)
SECOND_PERIOD_END_DELTA = datetime.timedelta(seconds=0)


class NoDataError(RuntimeError):
    pass


class DropDetector(detectors.Detector):
    def __init__(
            self,
            normal_range: Tuple["datetime.datetime", "datetime.datetime"],
            compare_range: Tuple["datetime.datetime", "datetime.datetime"]
    ):
        self.normal_range = normal_range
        self.compare_range = compare_range

    def detect(self, document: eod_prices.EodDataFile) -> float:
        data = document.data

        first_average = _get_avg_in_range(data, from_date=self.normal_range[0], to_date=self.normal_range[1])
        second_average = _get_avg_in_range(data, from_date=self.compare_range[0], to_date=self.compare_range[1])

        if not first_average or not second_average:
            _logger.info(f"No data in range for {document.ticker}", extra={
                "first_average": first_average,
                "second_average": second_average,
                "first_range": self.normal_range,
                "second_range": self.compare_range
            })
            return 0.0

        drop_percentage = abs((second_average - first_average) / first_average)
        return -drop_percentage


def _get_avg_in_range(data, from_date=None, to_date=None):
    entries = list(filter(stream_filters.RangeFilter(from_date, to_date).is_valid, data))
    if not entries:
        return None
    return sum(map(lambda e: e.close, entries)) / len(entries)


def run_analysis(event: events.EodUpdateSNSEvent):
    document = _get_document(event.ticker)

    data = list(_filter_data(document.data))
    if not _meets_requirements(data):
        _logger.info(f"Ticker {event.ticker} does not meet drop requirements")
        return

    now = datetime.datetime.utcnow()
    potential_gain = DropDetector(
        (now - FIRST_PERIOD_START_DELTA, now - FIRST_PERIOD_END_DELTA),
        (now - SECOND_PERIOD_START_DELTA, now - SECOND_PERIOD_END_DELTA)
    ).detect(document)

    if potential_gain < 0:
        _logger.info(f"No drop ({potential_gain})")
        return
    elif potential_gain < MIN_PERCENTAGE:
        _logger.info(f"Drop is too small ({potential_gain})")
        return

    sns.publish(
        CONFIG.SNS_TRADE_SIGNAL_TOPIC_ARN,
        events.TradeSignalEvent.new(ticker=event.ticker, predicted_change=potential_gain, source="DropDetection")
    )


def _get_document(ticker: models.Ticker) -> eod_prices.EodDataFile:
    _logger.info(f"Running drop detection on {ticker}")
    document = eod_prices.get_eod_price_file(ticker)
    if not document or not document.data:
        _logger.error(f"No data for {ticker}")
        raise NoDataError(ticker)
    return document


def _filter_data(data: Iterable[eod_historical_data.EodDataEntry]) -> Iterable[eod_historical_data.EodDataEntry]:
    return stream_filters.apply_filters(data, [
        stream_filters.HasValueFilter("close"),
        stream_filters.AfterDateFilter(datetime.datetime.utcnow() - FIRST_PERIOD_START_DELTA)
    ])


def _meets_requirements(data: List[eod_historical_data.EodDataEntry]) -> bool:
    if not data:
        _logger.info(f"No data")
        return False

    if not set_filter.IsAverageVolumeAboveMinimumFilter(MIN_AVERAGE_VOLUME).is_valid(data):
        _logger.info(f"Not enough volume")
        return False

    if not set_filter.MaxMinSpreadMinimumFilter(MIN_SPREAD).is_valid(data):
        _logger.info(f"Not enough variance in price")
        return False

    return True
