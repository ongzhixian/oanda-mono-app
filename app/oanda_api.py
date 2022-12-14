import json

from datetime import datetime
from os import path, makedirs
from urllib.request import urlopen as url_open
from urllib.request import Request as url_request
from urllib.parse import urlencode
import time

from logger import Logger

log = Logger()

class OandaApi(object):
    def __init__(self, settings, output_path):
        self.account_id = settings['account_number']
        self.api_key = settings['api_key']
        self.rest_api_url = settings['rest_api_url']
        self.streaming_api_url = settings['streaming_api_url']
        self.output_path = output_path
        self.headers={
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        required_sub_directories = [ 'instruments', 'historical-candles' ]
        for sub_directory in required_sub_directories:
            directory_path = path.join(self.output_path, sub_directory)
            full_path = path.abspath(directory_path)
            if not path.exists(full_path):
                try:
                    makedirs(full_path)
                except Exception:
                    log.error(f"ERROR - output path does not exists {full_path}")
                    exit(2)


    def save_instruments_json_data_to_file(self, data):
        FILE_DATETIME = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        FILE_NAME = f'instrument-{FILE_DATETIME}.json'
        SAVE_FILE_PATH = path.join(self.output_path, 'instruments', FILE_NAME)
        with open(SAVE_FILE_PATH, 'w', encoding='utf-8') as out_file:
            out_file.write(data)

    def get_account_instruments(self):
        """
        Get account instruments
        """
        account_id = self.account_id
        url = f"{self.rest_api_url}/v3/accounts/{account_id}/instruments"

        request = url_request(
            url, 
            data=None, 
            headers=self.headers
        )
        
        with url_open(request) as response:
            response_data = response.read().decode("utf-8")
            self.save_instruments_json_data_to_file(response_data)
        try:
            response_json = json.loads(response_data)
            return response_json['instruments'] if 'instruments' in response_json else []
        except Exception as ex:
            log.warn(f"Invalid response_json; {ex}")
            return []


    def get_latest_candles(self, candle_spec='EUR_USD:S10:BM', account_id=None):
        """Not in use; this fetch just the latest candle for the given candle specification"""
        account_id = self.account_id if account_id is None else account_id
        url = f"{self.rest_api_url}/v3/accounts/{account_id}/candles/latest?candleSpecifications={candle_spec}"
        
        request = url_request(
            url, 
            data=None, 
            headers=self.headers
        )
        with url_open(request) as response:
            response_data = response.read().decode("utf-8")
            log.debug(response_data)
        try:
            response_json = json.loads(response_data)
            # normalized_candle_spec = candle_spec.replace(':','-')
            # self.dump_to_file(f'latest-candles-{normalized_candle_spec}.json', response_json)
            return response_json
        except Exception as ex:
            log.warn(f"Invalid response_json; {ex}")
            return None


    def save_historical_candle_json_data_to_file(self, data, instrument_name):
        FILE_DATETIME = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        FILE_NAME = f'historical-candle-{instrument_name}-{FILE_DATETIME}.json'
        SAVE_FILE_PATH = path.join(self.output_path, 'historical-candles', FILE_NAME)
        with open(SAVE_FILE_PATH, 'w', encoding='utf-8') as out_file:
            out_file.write(data)        


    def get_historical_candles(self, instrument_name, granularity='S10'):
        account_id = self.account_id
        url = f"{self.rest_api_url}/v3/accounts/{account_id}/instruments/{instrument_name}/candles?granularity={granularity}"

        request = url_request(
            url, 
            data=None, 
            headers=self.headers
        )
        print(self.headers)

        try:
            with url_open(request) as response:
                response_data = response.read().decode("utf-8")
                self.save_historical_candle_json_data_to_file(response_data, f"{instrument_name}-{granularity}")
        except Exception as err:
            print(err)

        try:
            response_json = json.loads(response_data)
            return response_json
        except Exception as ex:
            log.warn(f"Invalid response_json; {ex}")
            return None

    def get_test_historical_candles(self):
        with open('C:\data\oanda\historical-candles\historical-candle-XAU_USD-S10-20220917-233751.json', 'r', encoding='utf-8') as in_file:
            return json.load(in_file)

        
    def get_price_stream(self):
        account_id = self.account_id
        # curl \
        # -H "Authorization: Bearer <AUTHENTICATION TOKEN>" \
        # "https://stream-fxtrade.oanda.com/v3/accounts/<ACCOUNT>/pricing/stream?instruments=EUR_USD%2CUSD_CAD"
        candleSpecificationList = 'XAU_USD,EUR_USD'
        url = f"{self.streaming_api_url}/v3/accounts/{account_id}/pricing/stream?instruments=XAU_USD"

        stream_headers={
            'Authorization': f"Bearer {self.api_key}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
            'Content-Type': 'application/octet-stream'
        }

        request = url_request(
            url, 
            data=None, 
            headers=stream_headers
        )

        with url_open(request) as response:
            while (True):
                binary_response_data = response.read1()
                print(binary_response_data.decode("utf-8"))
                time.sleep(.1)
        

    def place_new_limit_order(self, quantity, instrument_name, price, take_profit, stop_loss):
        account_id = self.account_id
        url = f"{self.rest_api_url}/v3/accounts/{account_id}/orders"

        data = json.dumps({
            "order": {
                "units": str(quantity),
                "instrument": instrument_name,
                "price": str(price),
                "type": "LIMIT",	
                "timeInForce": "GTC",
                "positionFill": "DEFAULT",
                "stopLossOnFill": {
                    "timeInForce": "GTC",
                    "price": str(stop_loss)
                },
                "takeProfitOnFill": {
                    "price": str(take_profit)
                }
            }
        })

        print(data)

        jsondataasbytes = data.encode('utf-8')   # needs to be bytes

        request = url_request(
            url, 
            data=jsondataasbytes, 
            headers=self.headers,
            method="POST"
        )
        # request.add_header('Content-Length', len(jsondataasbytes))
        # request.add_header('Content-Type', 'application/json; charset=utf-8')

        try:
            with url_open(request) as response:
                response_data = response.read().decode("utf-8")       
        except Exception as err:
            print(err)
            print(err.file.read())

        try:
            response_json = json.loads(response_data)
            return response_json['orderCreateTransaction'] if 'orderCreateTransaction' in response_json else None
        except Exception as ex:
            log.warn(f"Invalid response_json; {ex}")
            return None
        

    def cancel_pending_order(self, transaction_id):
        account_id = self.account_id
        url = f"{self.rest_api_url}/v3/accounts/{account_id}/orders/{transaction_id}/cancel"

        request = url_request(
            url, 
            data=None, 
            headers=self.headers,
            method="PUT"
        )

        try:
            with url_open(request) as response:
                response_data = response.read().decode("utf-8")
                print(response_data)
        except Exception as err:
            print(err)
            print(err.file.read())

        # try:
        #     response_json = json.loads(response_data)
        #     return response_json
        # except Exception as ex:
        #     log.warn(f"Invalid response_json; {ex}")
        #     return None