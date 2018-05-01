from livecoin import LiveCoin
import traceback
import livecoin_attributes
import json
import time
import datetime
import os
import sys
from decimal import Decimal

# Создаем экземпляр класса LiveCoin
livecoin = LiveCoin(livecoin_attributes.api_key, livecoin_attributes.secret_key)


# Функция получаения данных
def get_pairs(func):
    # Указываем путь
    A = 'C:\\Users\\Сергей\\PycharmProjects\\bot\\preserved'

    entry = func((e for e in os.scandir(A) if e.is_file(follow_symlinks=False)),
                key=lambda e: getattr(e.stat(), 'st_birthtime', None) or e.stat().st_ctime)

    with open(entry.path, encoding='utf-8') as data_file:
        return json.loads(data_file.read())


# Основная функция
def main():
    # Получение купленных пар которые сейчас на аккаунте
    account_balances = livecoin.get_balances()

    # Те пары, для которых не над считать цену к доллару
    restricted_values = ['RUR', 'USD']

    # Проходим по всем парам на аккаунте
    for pair in account_balances:
        # Проверяем что на балансе содержится больше 0
        # Так же что валюта отнсится к типу total
        # И что валюта не тносится к валютам для которых не надо считать цену
        if pair['value'] > 0 and pair['type'] == 'total' and pair['currency'] not in restricted_values:
            # Делаем проверку на исключение,
            # чтобы нам вывдились тольк пары,
            # для которых пришел ответ от сервера
            try:
                # Получаем данные по паре с сервера
                data = livecoin.get_ticker(pair['currency'] + '/USD')
                # Цена пары к доллару
                price = Decimal(data['last'])
                # Считаем итог в формате цена * количество на аккаунте
                total_price = price * Decimal(pair['value'])
                # Вывдим с форматированием, чт total_price содержит 5 знаков псле запятой
                print("Price for {} with amount {} = {:.5}$".format(pair['currency'], pair['value'], total_price))
            except Exception as ex:
                # Ловим исключение и кладем его в переменную ex
                # Выводим исключение(ошибку)
                print(ex)
                print("No pair {}".format(pair["currency"] + "/USD"))

    # Получаем все пары с сервера
    all_pair = livecoin.get_tickers()

    # Генерируем названия файла с датой
    file_name = "{}.json".format(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d_%H-%M'))

    # Записываем данные в папку preserved и названием file_name.json
    with open(os.path.join(os.getcwd() + '\\preserved', file_name), "w", encoding="utf-8") as file:
        json.dump(all_pair, file)


    path = 'example.json'

    # Получаем все пары
    all_pairs = get_pairs(max)
    # Получаем пары из самого старого файла
    min_all_pairs = get_pairs(min)
    # Получаем пары из самого нового файла
    max_all_pairs = get_pairs(max)

    # Идем циклом сначала по минимальным
    # потом по максимальным парам
    for el_1 in min_all_pairs:
        for el_2 in max_all_pairs:
            # el_1 - минимальная пара
            # el_2 - максимальная пара
            # Сравниваем их пары
            if el_1["symbol"] == el_2["symbol"]:
                # Сравниваем их цены с нулем
                if el_2["last"] == 0 or el_1["last"] == 0:
                    continue
                # Получаем название минимальной пары
                symbol = el_1['symbol']
                # Считаем разницу в процентах
                diff = float(((el_2["last"] - el_1["last"]) / el_1["last"]) * 100)
                # Получаем цены для минимальной и максимальной
                mi = el_1["last"]
                ma = el_2["last"]

                # Выводим в определенном формате
                print("{0:15} {1:<6.2f}% {2:^3} {3:<15.6f} {4:^3} {5:<15.6f}".format(symbol, diff, "min", mi, "max", ma))
                break

    # нужно выгружать файл 1. С изменениями в процентном соотношении за день с 6:00 и на протяжение каждого часа до 24:00.
    #                      2. Еженедельное изменение в процентном соотношении с начала недели (тут нужно задать подсчет недель) и до f24:00 воскресения.
    #                      3. Ежемесячное изменение в процентном соотношении от первой даты до конца этого месяца(не полный месяц), и от начала и до конца следующих месяцев.
    #                      4. Привести к просчету всех данных и вывводу их в читаемом виде (предположительно в Excеl формате).
    #                      5. Запуска скрипта 2 раза в час за минуту до конца часа и с первой минуты нового часа.
    #                      6. Сортировка по максимально выросшим валютам и выводом топ 10 валют.


    ##


    translate = {
        "last": "Стоимость",
        "high": "максимальная стоимость за 24 ч.",
        "low": "минимальная стоимость за 24 ч.",
        "volume": "объем торгов за 24 ч.",
        "vwap": "средняя цена объема рынка",
        "max_bid": "максимальная цена покупки за 24 ч.",
        "min_ask": "минимальная цена продажи за 24 ч.",
        "best_bid": "минимальная цена покупки (в данный момент на рынке)",
        "best_ask": "Максимальная цена продажи (в данный момент на рынке)"
    }


    for pair in all_pair:
        pair_rus = pair['last']
        pair[translate['last']] = pair_rus
        del pair['last']
        pair_rus = pair['high']
        pair[translate['high']] = pair_rus
        del pair['high']
        pair_rus = pair['low']
        pair[translate['low']] = pair_rus
        del pair['low']
        pair_rus = pair['volume']
        pair[translate['volume']] = pair_rus
        del pair['volume']
        pair_rus = pair['vwap']
        pair[translate['vwap']] = pair_rus
        del pair['vwap']
        pair_rus = pair['max_bid']
        pair[translate['max_bid']] = pair_rus
        del pair['max_bid']
        pair_rus = pair['min_ask']
        pair[translate['min_ask']] = pair_rus
        del pair['min_ask']
        pair_rus = pair['best_bid']
        pair[translate['best_bid']] = pair_rus
        del pair['best_bid']
        pair_rus = pair['best_ask']
        pair[translate['best_ask']] = pair_rus
        del pair['best_ask']

        #print(pair)

    print("Success")


if __name__ == '__main__':
    # бесконечный цикл
    while True:
        try:
            # Пробуем запустить main
            main()
            # Ждем 3600 секунд
            time.sleep(3600)
        except Exception as ex:
            # main запустить не удалось
            # поулчили исключение
            # выводим его и ждем 60 секунд
            print(ex)
            traceback.print_exc()
            time.sleep(60)
