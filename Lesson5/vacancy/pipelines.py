"""Модуль содержит класс для сохранения данных в базу данных."""

from itemadapter import ItemAdapter
from pymongo import MongoClient


class VacancyPipeline:
    """Класс для сохранения данных в базу данных."""

    collection_name = 'hhru_vacancies'

    def __init__(self):

        self.mongo_uri = ('localhost', 27017)
        self.mongo_db = 'vacancies_db'
    
    def open_spider(self, spider):
        self.client = MongoClient(*self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):

        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
