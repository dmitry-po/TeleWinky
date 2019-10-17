# coding: utf-8
import requests


class TinkiVinki:
    def __init__(self, use_proxy=False):
        self.offset = self.__get_params__()
        base_url = 'https://api.telegram.org/bot'
        token = self.__get_token__()
        self.url = base_url + token
        self.data = {'offset': self.offset, 'limit': 1, 'timeout': 1}

        # proxy parameters
        self.use_proxy = use_proxy
        self.proxy = {}
        self.proxies_list = []
        if self.use_proxy:
            self.__get_proxies__()


    def __get_params__(self):
        with open('updateid.tg', 'r') as f:
            return (int(f.readline()))

    def __get_token__(self):
        with open('token.tg', 'r') as f:
            return f.readline().strip()

    def __get_proxies__(self):
        proxies_list = []
        try:
            with open('proxies.tg', 'r') as f:
                for line in f:
                    proxy = {}
                    for i in line.strip('\n').split(','):
                        proxy[i.split(':')[0]] = ':'.join(i.split(':')[1:])
                    proxies_list.append(proxy)
        except FileNotFoundError:
            self.use_proxy = False
            proxies_list = []
        self.proxies_list = proxies_list
        print(self.proxies_list)

    def __search_valid_proxy__(self):
        print('Looking for valid proxy')
        for proxy in self.proxies_list:
            self.proxy = proxy
            print(f'Trying {proxy}')
            try:
                request = requests.get(self.url + '/getME',
                             proxies=self.proxy)
                print(request.json()['ok'])
                print(f'Valid proxy found: {proxy}')
                break
            except Exception as e:
                pass

    def __save_params__(self):
        with open('updateid.tg', 'w') as f:
            f.write(str(self.offset))

    def check_updates(self):
        self.data = {'offset': self.offset, 'limit': 1, 'timeout': 30}
        try:
            request = requests.post(self.url + '/getUpdates',
                                    data=self.data,
                                    proxies=self.proxy)
            print(request.text)
        except Exception as e:
            print(f'Error getting updates: {e}')
            raise ConnectionError(e)
        return request.json()['result']

    def process_updates(self, updates):
        message = ''
        for update in updates:
            self.offset = int(update['update_id']) + 1

            # Прерывать обработку при получении не текстовых сообщений.
            if 'message' not in update or 'text' not in update['message']:
                print('Unknown message')
                continue

            message = f"Сам ты {update['message']['text']}"
        return message

    def send_message(self, update, reply_text, **kwargs):
        message_data = {  # формируем информацию для отправки сообщения
            'chat_id': update['message']['chat']['id'],  # куда отправляем сообщение
            'text': reply_text,  # само сообщение для отправки
            # 'reply_to_message_id': update['message']['message_id'],   # если параметр указан, то бот отправит сообщение в reply
            'parse_mode': 'HTML',  # про форматирование текста ниже
            'reply_markup': kwargs['inline_button'] if kwargs != {} else ''
        }

        try:
            request = requests.post(self.url + '/sendMessage', data=message_data,
                                    proxies=self.proxy)  # запрос на отправку сообщения
        except:
            print('Send message error')

    def run(self):
        try:
            updates = self.check_updates()
            reply = self.process_updates(updates)
            self.send_message(updates, reply)
        except KeyboardInterrupt:
            message = 'Interrupted by the user'
            print(message)
            self.__save_params__()
            raise KeyboardInterrupt(message)
        except ConnectionError:
            print('Network problem')
            if self.use_proxy:
                self.__search_valid_proxy__()



if __name__ == "__main__":
    tb = TinkiVinki(use_proxy=True)
    while True:
        tb.run()
