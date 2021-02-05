"""Паук для сбора картинок, для которые характеризуются в Instagram заданным
тегом."""

import json
import scrapy
from ..loader import InstagramLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    URL = 'https://www.instagram.com/'
    start_urls = [URL]
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    ITEMS = ['data', 'date', 'url']

    def __init__(self, username, enc_password, *args, **kwargs):
        """Конструктор паука.
        :param username: логин пользователя;
        :param enc_password: закодированный пароль пользователя."""

        # Теги, по которым будут искаться картинки
        self.TAGS = ['development', 'python']
        self.USERNAME = username
        self.ENC_PASSWORD = enc_password
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_csrf(response):
        """Метод возвращает CSRF-токен форм страницы.
        :param response: ответ типа Response модуля scrapy.
        :return: CSRF-токен."""

        script = response.xpath(
            '//body/script[contains(text(), "csrf_token")]/text()').get()
        json_data = json.loads(script.replace(
            'window._sharedData = ', '')[:-1])
        return json_data['config']['csrf_token']

    @staticmethod
    def make_url(tag, end_cursor=''):
        """Метод создает url-адрес для запроса страницы с картинками.
        :param tag: тег, для которого нужно найти картинки;
        :param end_cursor: курсор на конец текущей страницы с картинками.
        :return: относительный url-адрес для запроса."""

        p = 'query_hash=9b498c08113f1e09617a1703c22b2f32&variables={"tag_name":"' +\
            tag + '","first":30'
        if end_cursor:
            p += ',"after":"' + end_cursor + '"'
        p += '}'
        return f'graphql/query/?{p}'

    def parse(self, response):
        """Метод парсинга данных при авторизации."""

        try:
            # Готовим форму и заголовок для авторизации
            form_data = {
                'username': self.USERNAME,
                'enc_password': self.ENC_PASSWORD,
            }
            headers = {'x-csrftoken': self.get_csrf(response)}
            yield scrapy.FormRequest(
                self.LOGIN_URL, method='POST', formdata=form_data,
                headers=headers, callback=self.parse)
        except AttributeError:
            if response.json()['authenticated']:
                # Авторизация прошла успешно
                scrapy.http.Response.url = self.URL
                for tag in self.TAGS:
                    # Запрашиваем страницу с картинками с тегом tag
                    url = self.make_url(tag)
                    yield response.follow(url, method='GET',
                                          callback=self.parse_tag,
                                          cb_kwargs={'tag': tag})

    def parse_tag(self, response, tag):
        """Метод для сбора данных со страницы с картинками с определенным
        тегом.
        :param tag: тег картинки."""

        p = response.json()['data']['hashtag']['edge_hashtag_to_media']
        # Получаем информацию о странице: курсор конца и есть ли страница
        # после данной страницы
        end_cursor = p['page_info']['end_cursor']
        has_next_page = p['page_info']['has_next_page']
        if has_next_page:
            # Есть еще страницы с картинками
            url = self.make_url(tag, end_cursor)
            yield response.follow(url, method='GET', callback=self.parse_tag,
                                  cb_kwargs={'tag': tag})
        # Собираем данные о картинках на этой странице
        for node in p['edges']:
            loader = InstagramLoader()
            for item in self.ITEMS:
                loader.add_value(item, node['node'])
            yield loader.load_item()
