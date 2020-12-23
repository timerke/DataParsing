import json
import requests
import time
from pathlib import Path


def get_response(url, **args):
    """Функция выполняет запросы GET по заданному адресу.
    :param url: адрес;
    :param args: дополнительные параметры запроса.
    :return: ответ на запрос."""

    while True:
        try:
            r = requests.get(url, args)
            if r.status_code != 200:
                raise Exception
        except Exception:
            time.sleep(0.5)
        time.sleep(0.05)
        return r


def save(filename, data):
    """Функция сохраняет данные в файл.
    :param filename: имя файла;
    :param data: данные для записи."""

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


class Product_parser:
    """Класс для сбора данных о товарах."""

    # Заголовок
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 \
        Safari/537.36'}

    def __init__(self, url, mode=False):
        """Конструктор класса.
        :param url: стартовый адрес;
        :param mode: режим, в котором должен работать парсер."""

        self.START_URL = url
        if mode:
            # Парсер должен возвращать данные
            self.mode = True
        else:
            # Парсер должен самостоятельно сохранять данные в файлы
            self.mode = False

    def parse(self, url):
        """Метод-генератор возвращает данные о товарах.
        :param url: адрес, по которому нужно получить данные о товарах.
        :return: словарь с данными о товаре."""

        while url:
            r = get_response(url, headers=self.HEADERS)
            r = r.json()
            url = r['next']
            for product in r['results']:
                yield product

    def run(self):
        """Метод запускает сбор данных."""

        for product in self.parse(self.START_URL):
            if self.mode:
                # Парсер работает на возвращение данных в режиме генератора
                yield product
            else:
                # Парсер работает на самостоятельное сохранение данных в файлы
                filename = Path(__file__).parent.joinpath('products',
                                                          f'{product.id}.json')
                save(filename, product)


class Category_parser():
    """Класс для сбора данных о категориях товаров."""

    # Заголовок
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 \
        Safari/537.36'}

    def __init__(self, url):
        """Конструктор класса.
        :param url: адрес запроса для получения данных о категориях."""

        self.URL = url

    def parse(self):
        """Метод-генератор возвращает данные о категориях товаров.
        :return: словарь с кодом и именем категории."""

        r = get_response(self.URL, headers=self.HEADERS)
        for category in r.json():
            yield category

    def run(self):
        """Метод запускает сбор данных."""

        for category in self.parse():
            # Получаем код и название категории
            code = category['parent_group_code']
            name = category['parent_group_name']
            # Делаем запрос для получения всех данных о товарах из
            # рассматриваемой категории
            url = f'https://5ka.ru/api/v2/special_offers/?categories={code}'
            product_parser = Product_parser(url, True)
            # Получаем список товаров из категории
            products = [product for product in product_parser.run()]
            # Создаем конечный объект с данными о категории
            data = {'code': code, 'name': name, 'products': products}
            # Записываем данные в файл
            filename = Path(__file__).parent.joinpath('categories',
                                                      f'{name}.json')
            save(filename, data)


if __name__ == '__main__':
    parser = Product_parser('https://5ka.ru/api/v2/special_offers/')
    parser.run()

    parser2 = Category_parser('https://5ka.ru/api/v2/categories/')
    parser2.run()
