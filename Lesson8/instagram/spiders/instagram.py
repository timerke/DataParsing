"""Пояснение, как работает паук.
Пауку нужно задать исходного пользователя. Паук найдет всех подписчиков
данного пользователя. Затем найдет всех подписчиков подписчиков и т.д. В итоге
будет собрана база данных из пользователей, которые подписаны хотя бы на одного
другого пользователя. В pipeline найдем пользователей, которые подписаны друг
на друга и получим таблицу с рукопожатиями: таблицу пользователей, которые
подписаны друг на друга и могут участвовать в цепочке рукопожатий. После этого
останется проанализировать таблицы знакомых друг с другом пользователей и найти
цепочку от исходного пользователя до конечного пользователя (который пока не
фигурировал в исследовании). Делаем это с помощью алгоритма поиска в ширину."""

import json
import scrapy
from ..loader import SubscriptionLoader, UserLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    URL = 'https://www.instagram.com/'
    start_urls = [URL]
    # Адрес для авторизации в Instagram
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    # Поля модели UserItem
    USER_ITEMS = ('username', 'full_name', 'user_instagram_id', 'date')
    # Поля модели SubscriptionItem
    SUBSCRIPT_ITEMS = ('follower_id', 'following_id')
    # Хэш запроса для определения подписчиков
    QUERY_HASH = '5aefa9893005572d237da5068082d8d5'

    def __init__(self, username, enc_password, start_user, *args, **kwargs):
        """Конструктор паука.
        :param username: логин пользователя;
        :param enc_password: закодированный пароль пользователя;
        :param start_user: логин исходного пользователя. С него начинается сбор
        данных о подписчиках пользователей."""

        # Логин исходного пользователя
        self.START_USER = start_user
        # Данные для входа в Instagram: логин и закодированный пароль
        self.USERNAME = username
        self.ENC_PASSWORD = enc_password
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_json(response):
        """Метод возвращает json-данные из страницы.
        :param response: ответ типа Response модуля scrapy.
        :return: json-данные."""

        script = response.xpath(
            '//body/script[contains(text(), "csrf_token")]/text()').get()
        json_data = json.loads(script.replace(
            'window._sharedData = ', '')[:-1])
        return json_data

    @staticmethod
    def make_url(user_id, query_hash, end_cursor=''):
        """Метод создает url-адрес для запроса подписок или подписчиков
        пользователя.
        :param user_id: Id пользователя, подписки или подписчиков которого
        нужно получить;
        :param query_hash: хэш требуемого запроса;
        :param end_cursor: курсор на конец текущей страницы.
        :return: относительный url-адрес для запроса."""

        p = 'query_hash=' + query_hash + '&variables={"id":"' + user_id + \
            '","include_reel":true,"fetch_mutual":false,"first":30'
        if end_cursor:
            p += ',"after":"' + end_cursor + '"'
        p += '}'
        return f'graphql/query/?{p}'

    def parse(self, response):
        """Метод парсинга данных при авторизации.
        :param response: объект типа Response из scrapy."""

        try:
            # Готовим форму и заголовок для авторизации
            form_data = {
                'username': self.USERNAME,
                'enc_password': self.ENC_PASSWORD,
            }
            csrftoken = self.get_json(response)['config']['csrf_token']
            headers = {'x-csrftoken': csrftoken}
            yield scrapy.FormRequest(
                self.LOGIN_URL, method='POST', formdata=form_data,
                headers=headers, callback=self.parse)
        except AttributeError:
            if response.json()['authenticated']:
                # Авторизация прошла успешно, получаем информацию о стартовом
                # пользователе
                scrapy.http.Response.url = self.URL
                yield response.follow(self.START_USER, method='GET',
                                      callback=self.parse_user)

    def parse_followers(self, response, user_id):
        """Метод для сбора данных о подписчиках исследуемого пользователя.
        :param response: объект типа Response из scrapy;
        :param user_id: Id пользователя, данные о подписках/подписчиках
        которого собираются."""

        try:
            data = response.json()['data']['user']['edge_followed_by']
        except:
            return
        # Подписчики пользователя
        for edge in data['edges']:
            # Данные о подписчике как о пользователе
            loader = UserLoader()
            for item in self.USER_ITEMS:
                loader.add_value(item, edge)
            yield loader.load_item()
            # Данные о факте подписки
            follower_id = edge['node']['id']
            follower = edge['node']['username']
            loader = SubscriptionLoader()
            for item in self.SUBSCRIPT_ITEMS:
                loader.add_value(item, {'user_id': user_id,
                                        'follower_id': follower_id})
            yield loader.load_item()
            # Берем исследованного подписчика и начинаем собирать данные о его
            # подписчиках
            url = self.make_url(follower_id, self.QUERY_HASH)
            yield response.follow(url, method='GET', callback=self.parse_followers,
                                  cb_kwargs={'user_id': follower_id})
        # Проверяем, есть ли допольнительные страницы с подписчиками/подписками
        end_cursor = None
        if data['page_info']['has_next_page']:
            # Дополнительные страницы есть, делаем запросы на них
            end_cursor = data['page_info']['end_cursor']
            url = self.make_url(user_id, self.QUERY_HASH, end_cursor)
            yield response.follow(
                url, method='GET', callback=self.parse_followers,
                cb_kwargs={'user_id': user_id})

    def parse_user(self, response):
        """Метод для сбора данных со страницы пользователя.
        :param response: объект типа Response из scrapy."""

        # Получаем данные исследуемого пользователя (Id, логин и полное имя)
        data = self.get_json(response)
        user_id = data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        loader = UserLoader()
        for item in self.USER_ITEMS:
            loader.add_value(item, data)
        yield loader.load_item()
        # Получаем подписчиков пользователя
        url = self.make_url(user_id, self.QUERY_HASH)
        yield response.follow(url, method='GET', callback=self.parse_followers,
                              cb_kwargs={'user_id': user_id})
