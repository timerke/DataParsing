"""Паук проходит по произвольному списку имен пользователей Instagram. В единую
структуру собираются данные о том, на кого подписан пользователь и кто подписан
на пользователя."""

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
    # Список хэшей запросов
    QUERY_HASHES = {
        # Запрос для определения подписок
        'following': '3dec7e2c57367ef3da3d987d89f9dbc8',
        # Запрос для определения подписчиков
        'followers': '5aefa9893005572d237da5068082d8d5',
    }

    def __init__(self, username, enc_password, *args, **kwargs):
        """Конструктор паука.
        :param username: логин пользователя;
        :param enc_password: закодированный пароль пользователя."""

        # Список пользователей, подписки и подписчиков которых нужно собрать
        self.USERS = ('yanna_lev',)
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
                # Авторизация прошла успешно, проходим по списку исследуемых
                # пользователей
                scrapy.http.Response.url = self.URL
                for user in self.USERS:
                    yield response.follow(user, method='GET',
                                          callback=self.parse_user)

    def parse_followers(self, response, user_id, query):
        """Метод для сбора данных о подписках или подписчиках исследуемого
        пользователя.
        :param response: объект типа Response из scrapy;
        :param user_id: Id пользователя, данные о подписках/подписчиках
        которого собираются;
        :param query: если following, то сбор данных о подписках, если
        followers, то сбор данных о подписчиках."""

        try:
            if query == 'followers':
                data = response.json()['data']['user']['edge_followed_by']
            else:
                data = response.json()['data']['user']['edge_follow']
        except:
            return
        # Получаем данные о подписке/подписчике
        for edge in data['edges']:
            # Данные о подписке/подписчике как о пользователе
            loader = UserLoader()
            for item in self.USER_ITEMS:
                loader.add_value(item, edge)
            yield loader.load_item()
            # Данные о факте подписки
            follow_id = edge['node']['id']
            loader = SubscriptionLoader()
            for item in self.SUBSCRIPT_ITEMS:
                loader.add_value(item, {'query': query,
                                        'user_id': user_id,
                                        'follow_id': follow_id})
            yield loader.load_item()
        # Проверяем, есть ли допольнительные страницы с подписчиками/подписками
        end_cursor = None
        if data['page_info']['has_next_page']:
            # Дополнительные страницы есть, делаем запросы на них
            end_cursor = data['page_info']['end_cursor']
            url = self.make_url(user_id, self.QUERY_HASHES[query], end_cursor)
            yield response.follow(
                url, method='GET', callback=self.parse_followers,
                cb_kwargs={'user_id': user_id, 'query': query})

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
        # Получаем подписки и подписчиков пользователя
        for query, hash in self.QUERY_HASHES.items():
            url = self.make_url(user_id, hash)
            yield response.follow(
                url, method='GET', callback=self.parse_followers,
                cb_kwargs={'user_id': user_id, 'query': query})
