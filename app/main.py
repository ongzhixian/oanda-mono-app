import json
import logging
import sys

from datetime import datetime
from os import path
from urllib.parse import quote
from urllib.request import urlopen as url_open
from urllib.request import Request as url_request

import pandas as pd

from logger import Logger
from program_arguments import get_settings_from_arguments
from program_signals import wait_for_sigterm
from oanda_api import OandaApi
import time

def setup_logging():
    logging.getLogger('pika').setLevel(logging.WARNING)
    log = Logger()
    return log


def analyse(json_data):
    candles = json_data['candles']
    flatten_data = [
    [ 
        datetime.strptime(x['time'], "%Y-%m-%dT%H:%M:%S.%f000Z"), 
        bool(x['complete']), 
        int(x['volume']), 
        float(x['mid']['o']), 
        float(x['mid']['h']), 
        float(x['mid']['l']), 
        float(x['mid']['c'])
    ] for x in candles]
    df = pd.DataFrame(
        flatten_data, 
        columns=['time','complete', 'Volume', 'Open', 'High', 'Low', 'Close'])

    print(f"df shape: {df.shape}")


    
if __name__ == "__main__":
    log = setup_logging()
    (oanda_settings, output_path, instruments_to_trade) = get_settings_from_arguments()
    oanda_api = OandaApi(oanda_settings, output_path)
    
    # Steps
    # oanda_api.get_account_instruments()
    # historical_candles_json = oanda_api.get_historical_candles(instruments_to_trade)
    
    # The real work-in-progress
    historical_candles_json = oanda_api.get_test_historical_candles()
    analyse(historical_candles_json)
    orderCreateTransaction = oanda_api.place_new_limit_order(1, "XAU_USD", 1680.000, 1680.020, 1679.970)
    time.sleep(10)
    oanda_api.cancel_pending_order(orderCreateTransaction['id'])

    # listen_for_tickers(url_parameters)
    # wait_for_sigterm()
    log.info("Program complete", source="program", event="complete")
