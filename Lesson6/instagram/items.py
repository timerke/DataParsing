"""Модуль с моделью данных, которые будут сохранены в базу данных."""

import scrapy


class InstagramItem(scrapy.Item):
    
    # Id
    _id = scrapy.Field()
    # Данные о посте из Instagram
    data = scrapy.Field()
    # Дата парсинга
    date = scrapy.Field()
    # Путь к сохраненной картинке
    image = scrapy.Field()
    # Ссылка на картинку
    url = scrapy.Field()
