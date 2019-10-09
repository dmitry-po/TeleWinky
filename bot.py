# coding: utf-8

import requests


class TinkiVinki:
    def __init__(self):
        self.offset = self.get_params()
        self.URL = 'https://api.telegram.org/bot'  # URL на который отправляется запрос
        self.TOKEN = self.get_token()
        self.proxies = {'http': '118.27.5.147:3128', 'https': '118.27.5.147:3128'}

    def get_params(self):
        with open('updateid.tg', 'r') as f:
            return (int(f.readline()))

    def get_token(self):
        with open('token.tg', 'r') as f:
            return f.readline()

    def save_params(self):
        with open('updateid.tg', 'w') as f:
            f.write(str(self.offset))

    def check_updates(self):
        data = {'offset': self.offset, 'limit': 1, 'timeout': 0}
        try:
            request = requests.post(self.URL + self.TOKEN + '/getUpdates', data=data,
                                    proxies=self.proxies)  # собственно сам запрос
            print(request.text)
        except Exception as e:
            print(f'Error getting updates: {e}')
            raise (e)

        for update in request.json()['result']:
            self.offset = int(update['update_id']) + 1  # подтверждаем текущее обновление

            if 'message' not in update or 'text' not in update[
                'message']:  # это просто текст или какая-нибудь картиночка?
                print('Unknown message')
                continue

            message_data = {  # формируем информацию для отправки сообщения
                'chat_id': update['message']['chat']['id'],  # куда отправляем сообщение
                'text': f"Сам ты {update['message']['text']}",  # само сообщение для отправки
                # 'reply_to_message_id': update['message']['message_id'],   # если параметр указан, то бот отправит сообщение в reply
                'parse_mode': 'HTML'  # про форматирование текста ниже
            }

            try:
                request = requests.post(self.URL + self.TOKEN + '/sendMessage', data=message_data,
                                        proxies=self.proxies)  # запрос на отправку сообщения
            except:
                print('Send message error')

    def run(self):
        while True:
            try:
                self.check_updates()
            except KeyboardInterrupt:  # порождается, если бота остановил пользователь
                print('Interrupted by the user')
                self.save_params()
                break


if __name__ == "__main__":
    tb = TinkiVinki()
    tb.run()
