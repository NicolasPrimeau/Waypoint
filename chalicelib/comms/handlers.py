import datetime
from typing import List

from chalicelib import events, models
from chalicelib.config import CONFIG
from chalicelib.services import sqs, sns


class TradeSignal(dict):
    @classmethod
    def new(cls, ticker: models.Ticker):
        return cls({
            "ticker": str(ticker),
            "signals": list()
        })

    @property
    def ticker(self) -> models.Ticker:
        return models.Ticker(self["ticker"])

    @property
    def signals(self) -> List:
        return self["signals"]


class TradeSignalEntry(dict):
    @classmethod
    def new(cls, source: str, predicted_change: float, creation_date: "datetime.datetime"):
        return cls({
            "source": source,
            "predicted_change": predicted_change,
            "creation_date": creation_date.isoformat()
        })

    @property
    def source(self) -> str:
        return self["source"]

    @property
    def predicted_change(self) -> float:
        return self["predicted_change"]

    @property
    def creation_date(self) -> "datetime.datetime":
        return datetime.datetime.fromisoformat(self["creation_date"])


def process_trade_signals():
    email_event = events.TradeSignalsEmailEvent.new()
    for message in sqs.iterate_messages(CONFIG.SQS_TRADE_SIGNAL_COMMS_QUEUE_URL):
        event = events.TradeSignalEvent(sqs.extract_sns_to_sqs_message(message))
        if str(event.ticker) not in email_event.signals:
            email_event.signals[str(event.ticker)] = TradeSignal.new(event.ticker)

        email_event.signals[str(event.ticker)].signals.append(TradeSignalEntry.new(
            source=event.source,
            predicted_change=event.predicted_change,
            creation_date=event.creation_datetime
        ))

    if email_event.signals:
        sns.publish(CONFIG.SNS_EMAIL_TOPIC_ARN, email_event)
    else:
        sns.publish(CONFIG.SNS_EMAIL_TOPIC_ARN, events.SNSEvent({
            "message": "Nothing to report!"
        }))
