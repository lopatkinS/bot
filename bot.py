import requests
import token_telegramm
from livecoin import LiveCoin
import livecoin_attributes
import time

# Указываем URL вместе с токеном
URL = 'https://api.telegram.org/bot{}/'.format(token_telegramm.token)
# создаем экземпляр класса LiveCoin с названием livecoin.
# параметрами указываем api_key и secret_key
livecoin = LiveCoin(livecoin_attributes.api_key, livecoin_attributes.secret_key)

# Получаем список пар
pairs = livecoin.get_pairs()

# Получаем обновления с сервера
def get_updates(offset):
    # создаем новый url в котором указан offset(смещение данных)
    url = URL + 'getUpdates?offset={}'.format(offset)
    # делаем GET запрос
    r = requests.get(url)
    # возвращаем JSON
    return r.json()

# Получаем сообщения
def get_message(offset):
    # Данные которые вернул сервер
    data = get_updates(offset)

    # Если пустые возвращаем None
    if data['result'] == []:
        return None

    # Берем из последнего сообщения данные которые нам нужны
    chat_id = data['result'][-1]['message']['chat']['id']
    message_text = data['result'][-1]['message']['text']
    user_name = data['result'][-1]['message']['chat']['first_name']
    update_id = data['result'][-1]['update_id']

    # Создаем словарь с значениями которые нам нужны
    message = {
        'chat_id': chat_id,
        'text': message_text,
        'user_name': user_name,
        'update_id': update_id
    }

    # Возвращаем значения
    return message


# Функция отправки сообщения, где нужно указать chat_id и text
# По умолчанию text='Секундочку...'
def send_message(chat_id, text='Секундочку...'):
    # Создаем url в котором заполняем chat_id и text
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    # Делаем GET запрос для отправки сообщения
    requests.get(url)


def main():
    # Указываем смещение 0
    offset = "0"
    # Бесконечный цикл
    while True:
        # Получаем сообщение от сервера
        message = get_message(offset)

        # Если сообщение не пусто
        if message:
            # Берем из него нужные поля
            chat_id = message['chat_id']
            text = message['text']
            offset = str(int(message["update_id"]) + 1)

            # Если текст сообщения в верхнем регистре (text.upper()) находится в парах
            if text.upper() in pairs:
                # Получаем данные с сервера для этой пары
                data = livecoin.get_ticker(text.upper())
                # Отправляем сообщение клиенту
                send_message(chat_id, str(data['last']) + text.upper().split('/')[1])
            else:
                # Отправляем что нужно указать пару
                send_message(chat_id, "Введите пару")
        # После каждой итерации спим 2 секунды
        time.sleep(2)

# Если мы запускаем конкретно этот файл
# То этот код будет выполнен
# Если мы его подключаем через import, то нет
if __name__ == '__main__':
    main()


