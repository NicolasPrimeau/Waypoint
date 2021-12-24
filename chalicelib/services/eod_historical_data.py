import logging
from typing import List

import datetime
import requests

from chalicelib import models
from chalicelib.config import CONFIG

DATE_FORMAT = "%Y-%m-%d"

_logger = logging.getLogger()


class EodDataEntry(dict):
    @property
    def date(self) -> "datetime.datetime":
        return datetime.datetime.strptime(self["date"], DATE_FORMAT)

    @property
    def open(self) -> float:
        return self["open"]

    @property
    def high(self) -> float:
        return self["high"]

    @property
    def low(self) -> float:
        return self["low"]

    @property
    def close(self) -> float:
        return self["close"]

    @property
    def adjusted_close(self) -> float:
        return self["adjusted_close"]

    @property
    def volume(self) -> int:
        return self["volume"]


def get_eod_data(ticker: models.Ticker, from_: "datetime.datetime", to: "datetime.datetime"
) -> List[EodDataEntry]:
    params = {
        "api_token": CONFIG.EOD_HISTORICAL_DATA_API_KEY,
        "fmt": CONFIG.EOD_HISTORICAL_DATA_DATA_FORMAT,
        "period": CONFIG.EOD_HISTORICAL_DATA_PERIOD,
        "order": CONFIG.EOD_HISTORICAL_DATA_ORDER,
        "from": from_.strftime(DATE_FORMAT),
        "to": to.strftime(DATE_FORMAT),
    }
    response = requests.get(
        f"https://eodhistoricaldata.com/api/eod/{str(ticker)}",
        params=params
    )

    if response.status_code == 404:
        _logger.error(f"Unknown ticker: {ticker}")
        return []

    if 300 <= response.status_code:
        _logger.error(f"{response.status_code}: {response.text}")
        raise RuntimeError()

    return list(map(EodDataEntry, response.json()))
