import json
import logging
import os

from chalicelib.services import secrets


_logger = logging.getLogger()


class AppConfig:
    APP_NAME = "Waypoint"

    STAGE = "dev"
    AWS_REGION = "ca-central-1"

    EOD_HISTORICAL_DATA_URL = "https://eodhistoricaldata.com/api/eod/"
    EOD_HISTORICAL_DATA_API_KEY = None
    EOD_HISTORICAL_DATA_DATA_FORMAT = "json"
    EOD_HISTORICAL_DATA_PERIOD = "d"
    EOD_HISTORICAL_DATA_ORDER = "a"

    S3_BUCKET = "np.waypoint"
    S3_TO_ETF_LIST_KEY = "to_etf_list.csv"
    S3_TICKET_INFO_FOLDER_KEY = "ticker_info"

    SNS_EOD_DATA_UPDATE_TOPIC_ARN = "arn:aws:sns:ca-central-1:357603364432:WAYPOINT_EOD_DATA_UPDATE"

    def __init__(self):
        self.load_secrets(f"{AppConfig.STAGE}/{AppConfig.APP_NAME}")

    def load_secrets(self, name: str):
        _logger.info(f"Importing {name}")
        data = json.loads(secrets.get_secrets(name, AppConfig.AWS_REGION))
        for key, val in data.items():
            setattr(self, key, val)


def get_config() -> AppConfig:
    return {
        "dev": AppConfig()
    }.get(os.getenv("stage"), AppConfig())


CONFIG = get_config()
