import datetime
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
    _logger.info("Received EOD data update event")


# 06h00 ET
@app.schedule(chalice.Cron(minutes=0, hours=11, day_of_month='*', month='*', day_of_week='?', year='*'))
def refresh_data(event):
    now = datetime.datetime.utcnow()
    eod_prices.update_all_to_etf_prices(from_=now - datetime.timedelta(days=2), to=now)
