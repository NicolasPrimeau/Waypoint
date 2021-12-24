import datetime
import json
import logging

import chalice

from chalicelib import utils
from chalicelib.config import CONFIG
from chalicelib.data import eod_prices

app = chalice.Chalice(app_name='waypoint')

utils.setup_logging()


_logger = logging.getLogger()


@app.route('/')
def index():
    return {'hello': 'world'}


@app.on_sns_message(topic=CONFIG.SNS_EOD_DATA_UPDATE_TOPIC_ARN.split(":")[-1])
def handle_eod_update_event(event):
    _logger.info("Received EOD data update event", extra={
        "event": event.to_dict()
    })


@app.on_sqs_message(queue=CONFIG.SQS_EOD_DATA_UPDATE_QUEUE_URL.split("/")[-1], batch_size=1)
def handle_refresh_eod_data_request(event):
    _logger.info("Received EOD data refresh event", extra={
        "event": event.to_dict()
    })
    for record in event:
        eod_prices.handle_refresh_event_request(eod_prices.EodDataRefreshSQSEvent(json.loads(record.body)))


# 06h00 ET
@app.schedule(chalice.Cron(minutes=0, hours=11, day_of_month='*', month='*', day_of_week='?', year='*'))
def refresh_data(event):
    now = datetime.datetime.utcnow()
    eod_prices.trigger_refresh_event_requests(from_=now - datetime.timedelta(weeks=52*3), to=now)
