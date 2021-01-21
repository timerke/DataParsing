"""Паук для сбора данных о вакансиях"""

import re
import scrapy
from vacancy.items import VacancyItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls =\
        ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    @staticmethod
    def _get_text(code):
        """Метод извлекает текст из html-кода.
        :param code: html-код.
        :return: текст."""

        text = re.sub(r'^<span [^>]*>', '', code)
        text = re.sub(r'</span>$', '', text)
        return text.replace('<!-- -->', '').replace(u'\xa0', ' ')
    
    @staticmethod
    def _get_description(code):
        """Метод извлекает текст из описания вакансии.
        :param code: html-код описания.
        :return: текст описания."""

        if not code:
            return code
        text = re.sub(r'^<div [^>]*>', '', code)
        text = re.sub(r'</div>$', '', text)
        text = text.replace('<!-- -->', '').replace(u'\xa0', ' ')
        text = re.sub(r'<[^>]*>', '', text)
        while True:
            text_new = text.replace('  ', ' ')
            if text_new == text:
                break
            text = text_new
        return text

    def parse(self, response):
        """Метод собирает данные со страницы со списком вакансий."""

        # Получаем список вакансий на странице
        vacancies = response.css('div.vacancy-serp-item \
            div.vacancy-serp-item__row_header \
            a.bloko-link::attr(href)').getall()
        for vacancy in vacancies:
            yield response.follow(vacancy, callback=self.parse_vacancy)
        # Получаем ссылку на следующую страницу с вакансиями
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').get()
        yield response.follow(next_page, callback=self.parse)

    def parse_company(self, response):
        """Метод собирает данные со страницы работодателя."""

        # Получаем список вакансий работодателя
        vacancies = response.css('div.company-vacancy-indent \
            div.vacancy-list-item div.vacancy-list-item__block_description\
            a.bloko-link::attr(href)').getall()
        # Переходим по ссылкам всех вакансий работодателя
        for vacancy in vacancies:
            yield response.follow(vacancy, callback=self.parse_vacancy)

    def parse_vacancy(self, response):
        """Метод собирает данные со страницы вакансии."""

        # Название вакансии
        title = response.css('div.vacancy-title h1::text').get()
        # Ссылка на страницу вакансии
        href = response.url
        # Оклад
        s = response.css('div.vacancy-title p.vacancy-salary span').get()
        salary = self._get_text(s)
        # Описание
        s = response.css('div.vacancy-description \
            div.vacancy-section div.g-user-content').get()
        description = self._get_description(s)
        # Ключевые навыки
        s = response.css('div.vacancy-description \
            div.vacancy-section div.bloko-tag-list \
            div.bloko-tag span').getall()
        skills = [self._get_text(item) for item in s]
        # Название работодателя
        s = response.css('div.vacancy-company__details \
            a.vacancy-company-name span.bloko-section-header-2').get()
        company_title = self._get_text(s)
        # Ссылка на работодателя
        s = response.css('div.vacancy-company__details \
            a.vacancy-company-name::attr(href)').get()
        company_href = response.urljoin(s)
        # Передаем собранные данные
        data = {'title': title, 'href': href, 'salary': salary,
                'description': description, 'skills': skills,
                'company_title': company_title, 'company_href': company_href}

        yield VacancyItem(**data)
        # Переходим на страницу работодателя
        if company_href:
            yield response.follow(company_href, callback=self.parse_company)
