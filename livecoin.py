import urllib
import json
import hashlib
import hmac
import httplib2
from http import client
from collections import OrderedDict


class LiveCoin:
    # Указывает сервер к которому обращаться
    server = "api.livecoin.net"

    def __init__(self, api_key, secret_key):
        # Это коснтруктор класса
        # Устанавливаем стандартные значения для переменных
        # и создаем новое HTTPS соединение с сервером
        self.api_key = api_key
        self.secret_key = secret_key
        self._create_connection()

    # Создаем HTTPS соединение с сервером
    def _create_connection(self):
        self.connection = client.HTTPSConnection(self.server)

    # Делаем запрос с типом GET или POST
    # Методом например /exchange/ticker
    # С закодированными данными encoded_data
    # И шапкой/заголовком запроса header
    def _create_request(self, type, method, encoded_data='', headers=None):
        self.connection.request(type, method + "?" + encoded_data, headers=headers)

    # Получаем запрос в JSON формате
    def _get_response(self):
        return json.loads(self.connection.getresponse().read().decode('utf-8'))

    # Закрываем соединение с сервером
    def _close_connection(self):
        self.connection.close()

    # Генерируем подпись для сообщения (т.к этого требует сервер)
    def _generate_sign(self, msg):
        return hmac.new(self.secret_key.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha256).hexdigest().upper()

    # Статический метод класса, который проверяем, что в полученных данных нет ошибки
    @staticmethod
    def _check_for_errors(data):
        # Проверяем что ключ success есть в data и data['success'] не пуст
        if "success" in data and not data["success"]:
            # Выбрасываем исключение с текстом data['errorMessage']
            raise Exception(data["errorMessage"])
        # В противном случае возвращаем данные
        return data

    # Метод который получает основную информацию по какой-то паре
    def get_ticker(self, pair):
        # Указываем метод
        method = "/exchange/ticker"
        # Создаем отсортированный словарь для пар ключ - значение
        data = OrderedDict([('currencyPair', pair)])
        # Кодируем данные для отправки
        encoded_data = urllib.parse.urlencode(data)

        # Заполняем заголовок апи ключем и подписанными encoded_data
        headers = {
            'Api-key': self.api_key,
            'Sign': self._generate_sign(encoded_data)
        }

        # Создаем соединение
        self._create_request("GET", method, encoded_data, headers)
        # Получаем данные
        data = self._get_response()
        # Закрываем соединение
        self._close_connection()
        # Проверяем что нет ошибок и возвращаем, в противном случае будет Exception
        return self._check_for_errors(data)

    def get_tickers(self):
        # Указываем метод
        method = "/exchange/ticker"

        # Заполняем заголовок
        headers = {
            'Api-key': self.api_key
        }

        # Создаем запрос
        self._create_request("GET", method, headers=headers)
        # Получаем данные
        data = self._get_response()
        # Закрываем соединение
        self._close_connection()
        # Проверяем что нет ошибок и возвращаем, в противном случае будет Exception
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

