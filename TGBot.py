# coding: utf-8
import requests
import json


class TeleWinki:
    def __init__(self, token, use_proxy=False):
        self.offset = self.__get_params__()
        base_url = 'https://api.telegram.org/bot'
        self.url = base_url + token
        self.data = {'offset': self.offset, 'limit': 1, 'timeout': 100}
        self.commands = {}
        self.handlers = []

        # proxy parameters
        self.use_proxy = use_proxy
        self.proxy = {}
        self.proxies_list = []
        if self.use_proxy:
            self.__get_proxies__()

    def __get_params__(self):
        with open('updateid.tg', 'r') as f:
            return (int(f.readline()))

    def __get_proxies__(self):
        proxies_list = []
        try:
            with open('proxies.tg', 'r') as f:
                proxies_list = json.load(f)
        except FileNotFoundError:
            self.use_proxy = False
        self.proxies_list = proxies_list
        print(self.proxies_list[:3])

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
        #print('check')
        self.data['offset'] = self.offset
        try:
            request = requests.post(self.url + '/getUpdates',
                                    data=self.data,
                                    proxies=self.proxy)
            print(request.json()['result'])
        except Exception as e:
            print(f'Error getting updates: {e}')
            raise ConnectionError(e)
        try:
            update = request.json()['result']
        except KeyError:
            update = {}
        return update

    def send_message(self, chat_id, reply_text, **kwargs):
        message_data = {
            'chat_id': chat_id,
            'text': reply_text,
            'parse_mode': 'HTML'
        }
        if kwargs != {}:
            for arg in kwargs:
                message_data[arg] = kwargs[arg]
        #print(message_data)
        try:
            request = requests.post(self.url + '/sendMessage',
                                    data=message_data,
                                    proxies=self.proxy)
        except ConnectionError:
            raise(e)
        except Exception as e:
            print('Send message error')
            print(e)

    def add_handlers(self, filter):
        def decorator(func):
            self.handlers.append({'function': func, 'filter': filter})
        return decorator

    def process_updates(self, update):
        print('process')
        print(f'Active handlers: {self.handlers}')
        for handler in self.handlers:
            if handler['filter'](update):
                handler['function'](update)

    def run(self):
        while True:
            try:
                updates = self.check_updates()
                for update in updates:
                    self.offset = update['update_id'] + 1
                    self.process_updates(update)
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
    app = TinkiVinki(use_proxy=True)
    @app.add_handlers(lambda x: True)
    def parrot(update):
        if 'message' in update and 'text' in update['message']:
            app.send_message(chat_id=update['message']['chat']['id'],
                             reply_text=update['message']['text'])
    app.run()