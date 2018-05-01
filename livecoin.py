import urllib
import json
import hashlib
import hmac
import httplib2
from http import client
from collections import OrderedDict


class LiveCoin:
    server = "api.livecoin.net"

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self._create_connection()

    def _create_connection(self):
        self.connection = client.HTTPSConnection(self.server)

    def _create_request(self, type, method, encoded_data='', headers=None):
        self.connection.request(type, method + "?" + encoded_data, headers=headers)

    def _get_response(self):
        return json.loads(self.connection.getresponse().read().decode('utf-8'))

    def _close_connection(self):
        self.connection.close()

    def _generate_sign(self, msg):
        return hmac.new(self.secret_key.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha256).hexdigest().upper()

    @staticmethod
    def _check_for_errors(data):
        if "success" in data and not data["success"]:
            raise Exception(data["errorMessage"])
        return data

    def get_ticker(self, pair):
        method = "/exchange/ticker"
        data = OrderedDict([('currencyPair', pair)])
        encoded_data = urllib.parse.urlencode(data)

        headers = {
            'Api-key': self.api_key,
            'Sign': self._generate_sign(encoded_data)
        }

        self._create_request("GET", method, encoded_data, headers)
        data = self._get_response()
        self._close_connection()
        return self._check_for_errors(data)

    def get_tickers(self):
        method = "/exchange/ticker"

        headers = {
            'Api-key': self.api_key
        }

        self._create_request("GET", method, headers=headers)
        data = self._get_response()
        self._close_connection()
        return self._check_for_errors(data)

    def get_pairs(self):
        method = "/exchange/all/order_book"

        headers = {
            "Api-key": self.api_key
        }
        self._create_request("GET", method, '', headers)
        data = self._get_response()
        self._close_connection()
        return data.keys()

    def get_balances(self):
        method = "/payment/balances"
        data = OrderedDict([])
        encoded_data = urllib.parse.urlencode(data)

        headers = {
            "Api-key": self.api_key,
            'Sign': self._generate_sign(encoded_data)
        }
        self._create_request("GET", method, encoded_data, headers)
        data = self._get_response()
        self._close_connection()
        return data

