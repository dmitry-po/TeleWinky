# coding: utf-8
import requests


class TinkiVinki:
    def __init__(self, use_proxy=False):
        self.offset = self.__get_params__()
        base_url = 'https://api.telegram.org/bot'
        token = self.__get_token__()
        self.url = base_url + token
        self.data = {'offset': self.offset, 'limit': 1, 'timeout': 1}
        self.commands = {}

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
        print('check')
        self.data = {'offset': self.offset, 'limit': 1, 'timeout': 1}
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

    def process_updates(self, update):
        print('process')
        print(f'Active commands: {self.commands}')
        if 'text' in update:
            if update['text'] in self.commands.keys():
                self.commands[update['text']](update)
        else:
            print('pass')
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

        try:
            request = requests.post(self.url + '/sendMessage',
                                    data=message_data,
                                    proxies=self.proxy)
        except:
            print('Send message error')

    def set_updates(self, rule):
        def decorator(func):
            self.commands[rule] = func

        return decorator

    def do_something(self):
        print('Voila')

    def run(self):
        while True:
            try:
                updates = self.check_updates()
                for update in updates:
                    self.offset = update['update_id'] + 1
                    self.process_updates(update['message'])
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
