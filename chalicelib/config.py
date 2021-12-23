import os


class AppConfig:

    EOD_HISTORICAL_DATA_API_KEY = None

    def __init__(self):
        pass


class ProdAppConfig(AppConfig):
    stage = "Prod"


def get_config() -> AppConfig:
    return {
        "prod": ProdAppConfig()
    }[os.getenv("stage")]


CONFIG = get_config()
