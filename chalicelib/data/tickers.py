import csv
from typing import Iterator

from chalicelib import models
from chalicelib.config import CONFIG
from chalicelib.services import s3


def iterate_toronto_etfs() -> Iterator[models.Ticker]:
    for entry in csv.DictReader(s3.get_file_data(CONFIG.S3_BUCKET, CONFIG.S3_TO_ETF_LIST_KEY).split("\n")):
        yield models.Ticker(entry["Root Ticker"], models.StockExchangeCode.Toronto)
