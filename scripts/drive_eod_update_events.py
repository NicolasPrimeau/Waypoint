from chalicelib import events
from chalicelib.config import CONFIG
from chalicelib.data import tickers
from chalicelib.services import sns


def main():
    for ticker in tickers.iterate_toronto_etfs():
        sns.publish(CONFIG.SNS_EOD_DATA_UPDATE_TOPIC_ARN, events.EodUpdateSNSEvent.new(ticker))
        return


if __name__ == '__main__':
    main()
