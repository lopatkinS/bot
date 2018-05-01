import requests
import token_telegramm
from livecoin import LiveCoin
import livecoin_attributes
import time

token =token_telegramm.token
URL = 'https://api.telegram.org/bot' + token + '/'
livecoin = LiveCoin(livecoin_attributes.api_key, livecoin_attributes.secret_key)

pairs = livecoin.get_pairs()


def get_updates(offset):
    url = URL + 'getUpdates?offset={}'.format(offset)
    r = requests.get(url)
    return r.json()


def get_message(offset):
    data = get_updates(offset)

    if data['result'] == []:
        return None

    chat_id = data['result'][-1]['message']['chat']['id']
    message_text = data['result'][-1]['message']['text']
    user_name = data['result'][-1]['message']['chat']['first_name']
    update_id = data['result'][-1]['update_id']

    message = {
        'chat_id': chat_id,
        'text': message_text,
        'user_name': user_name,
        'update_id': update_id
    }

    return message


def send_message(chat_id, text='Секундочку...'):
    url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
    requests.get(url)


def main():
    offset = "0"
    while True:
        message = get_message(offset)

        if message:
            chat_id = message['chat_id']
            text = message['text']
            offset = str(int(message["update_id"]) + 1)

            if text.upper() in pairs:
                data = livecoin.get_ticker(text.upper())
                send_message(chat_id, str(data['last']) + text.upper().split('/')[1])
            else:
                send_message(chat_id, "Введите пару")
        time.sleep(2)

if __name__ == '__main__':
    main()


