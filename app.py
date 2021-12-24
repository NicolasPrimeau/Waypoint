import datetime
import json
import logging

import chalice

from chalicelib import utils, events
from chalicelib.config import CONFIG
from chalicelib.data import eod_prices
from chalicelib import analysis
import chalicelib.analysis.drop
from chalicelib import comms
import chalicelib.comms.handlers


app = chalice.Chalice(app_name='waypoint')

utils.setup_logging()


_logger = logging.getLogger()


@app.on_sns_message(topic=CONFIG.SNS_EOD_DATA_UPDATE_TOPIC_ARN.split(":")[-1])
def handle_eod_update_event(event):
    _logger.info("Received EOD data update event", extra={
        "event": event.to_dict()
    })
    analysis.drop.run_analysis(events.EodUpdateSNSEvent(json.loads(event.message)))


@app.on_sqs_message(queue=CONFIG.SQS_EOD_DATA_UPDATE_QUEUE_URL.split("/")[-1], batch_size=1)
def handle_refresh_eod_data_request(event):
    _logger.info("Received EOD data refresh event", extra={
        "event": event.to_dict()
    })
    for record in event:
        eod_prices.handle_refresh_event_request(events.EodDataRefreshSQSEvent(json.loads(record.body)))


# Weekdays 06h00 ET
@app.schedule(chalice.Cron(minutes=0, hours=11, day_of_month='?', month='*', day_of_week='2-6', year='*'))
def refresh_data(_):
    now = datetime.datetime.utcnow()
    eod_prices.trigger_refresh_event_requests(from_=now - datetime.timedelta(days=2), to=now)


# Weekdays 07h00 ET
@app.schedule(chalice.Cron(minutes=0, hours=12, day_of_month='?', month='*', day_of_week='2-6', year='*'))
def communicate_trade_signals(_):
    comms.handlers.process_trade_signals()
