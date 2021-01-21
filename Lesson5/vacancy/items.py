"""Модуль содержит модели собираемых данных с сайта hh.ru."""

import scrapy


class VacancyItem(scrapy.Item):
    
    _id = scrapy.Field()
    # Название вакансии
    title = scrapy.Field()
    # Ссылка на вакансию
    href = scrapy.Field()
    # Оклад
    salary = scrapy.Field()
    # Описание
    description = scrapy.Field()
    # Ключевые навыки
    skills = scrapy.Field()
    # Название работодателя
    company_title = scrapy.Field()
    # Ссылка на страницу работодателя
    company_href = scrapy.Field()

    pass
