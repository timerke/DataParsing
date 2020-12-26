"""Парсер для сбора данных о товарах по акции из Магнита."""

import datetime
import requests
import urllib
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient


class Magnit_parser:
    """Класс для парсинга данных о товарах из Магнита."""

    _HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 \
            Safari/537.36"
    }

    def __init__(self, url):
        """Конструктор класса.
        :param url: адрес запроса."""

        self.URL = url  # адрес запроса для парсинга данных
        # Связываемся с базой данных в MongoDB
        client = MongoClient("localhost", 27017)
        db = client["magnit_db"]
        # В базе данные о продуктах будут записаны в таблицу products
        self.products_tbl = db.products
        # Удаляем все записи из таблицы products
        self.products_tbl.delete_many({})

    def get_dates(self, product):
        """Метод возвращает даты начала и конца акции.
        :param product: продукт (объект bs4), для которого нужно получить даты
        акции.
        :return: кортеж из начальной и конечной дат акции."""

        element = product.find(attrs={"class": "card-sale__date"})
        if element == None:
            return None, None
        # Даты начала и конца акции
        date_from = None
        date_to = None
        # Текущие месяц и год
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        for e in element.find_all("p"):
            date_str = e.string
            # Находим разделитель между датой и предлогом с/до
            i1 = date_str.find(" ")
            date_str = date_str[i1 + 1 :]
            # Находим разделить между днем и месяцем
            i2 = date_str.find(" ")
            # Получаем день, месяц и год
            day = int(date_str[:i2])
            month = self.get_month(date_str[i2 + 1 :])
            year = current_year
            if month < current_month:
                # Если месяц в акции меньше текущего месяца, то дата акции
                # относится к следующему году
                year += 1
            if e.string[:i1].lower() == "с":
                date_from = datetime.datetime(day=day, month=month, year=year)
            elif e.string[:i1].lower() == "до":
                date_to = datetime.datetime(day=day, month=month, year=year)
        return date_from, date_to

    def get_info(self, product):
        """Метод возвращает данные о товаре.
        :param product: продукт-объект bs4.
        :return: словарь формата
        {url: url товара, promo_name: имя акции, product_name: имя товара,
        old_price: старая цена, new_price: новая цена,
        image_url: ccылка на картинку, date_from: дата начала акции,
        date_to: дата конца акции}."""

        # Url товара
        url = urllib.parse.urljoin(self.URL, product.get("href"))
        # Имя акции
        promo_name = self.get_name(product, "card-sale__header")
        # Имя продукта
        product_name = self.get_name(product, "card-sale__title")
        # Старая цена
        old_price = self.get_price(product, "label__price_old")
        # Новая цена
        new_price = self.get_price(product, "label__price_new")
        # Url картинки
        image_url = product.find("img").get("data-src")
        image_url = urllib.parse.urljoin(self.URL, image_url)
        # Даты начала и конца акции
        date_from, date_to = self.get_dates(product)
        return {
            "url": url,
            "promo_name": promo_name,
            "product_name": product_name,
            "old_price": old_price,
            "new_price": new_price,
            "image_url": image_url,
            "date_from": date_from,
            "date_to": date_to,
        }

    @staticmethod
    def get_month(month):
        """Метод возвращает номер месяца.
        :param month: имя месяца по-русски.
        :return: номер месяца или None, если месяц с указанным именем не
        найден."""

        MONTHS = {
            "янв": 1,
            "фев": 2,
            "мар": 3,
            "апр": 4,
            "май": 5,
            "июн": 6,
            "июл": 7,
            "авг": 8,
            "сен": 9,
            "окт": 10,
            "ноя": 11,
            "дек": 12,
        }
        return MONTHS.get(month[:3].lower())

    @staticmethod
    def get_name(product, class_name):
        """Метод возвращает внутренний текст, содержащийся в блоке с указанным
        классом.
        :param product: объект bs4;
        :param class_name: имя класса искомого блока.
        :return: внутренний текст искомого блока."""

        element = product.find(attrs={"class": class_name})
        if element == None:
            return None
        return element.contents[0].string

    @staticmethod
    def get_price(product, class_name):
        """Метод возвращает цену.
        :param product: продукт (объект bs4), для которого нужно получить цену;
        :param class_name: имя класса блока, содержащего цену.
        :return: цена в руб или None, если цену найти не удалось."""

        element = product.find(attrs={"class": class_name})
        if element == None:
            return None
        # Получаем рубли
        rubles = element.find(attrs={"class": "label__price-integer"})
        if rubles == None:
            rubles = None
        else:
            try:
                rubles = int(rubles.string)
            except:
                return None
        # Получаем копейки
        pennies = element.find(attrs={"class": "label__price-decimal"})
        if pennies == None:
            pennies = None
        else:
            try:
                pennies = int(pennies.string) / 100
            except:
                pass
        return rubles + pennies

    def get_products(self):
        """Метод возвращает список объектов bs4, содержащих информацию о
        товарах.
        :return: список объектов bs4, представляющих товары."""

        r = requests.get(self.URL, headers=self._HEADERS)
        if r.status_code != 200:
            print("Не удалось получить данные")
        soup = bs(r.text, "lxml")
        return soup.find_all(attrs={"class": "card-sale_catalogue"})

    def run(self):
        """Метод запускает сборщик информации."""

        for product in self.get_products():
            data = self.get_info(product)
            self.products_tbl.insert_one(data)


if __name__ == "__main__":
    URL = "https://magnit.ru/promo/?geo=moskva"
    parser = Magnit_parser(URL)
    parser.run()
