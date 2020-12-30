"""Модуль для работы с базой данных."""

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database():
    """Класс для работы с базой данных."""

    def __init__(self, db_name):
        """Конструктор класса.
        :param db_name: имя базы данных для подключения."""

        # Подключение к базе данных и создание таблиц
        engine = create_engine(db_name)
        models.Base.metadata.create_all(engine)
        # Создаем сессию
        self.Session = sessionmaker(bind=engine)

    def save_data(self, data):
        """Метод сохраняет данные в базу данных.
        :param data: данные для сохранения."""

        session = self.Session()
        # Проверяем, есть ли в БД автор, если нет, то создаем его
        author_url = data['author']['url']
        author = session.query(models.Author).filter_by(url=author_url).first()
        if not author:
            author = models.Author(**data['author'])
        # Создаем запись в модель Post
        post = models.Post(**data['post'], author=author)
        # У поста могут быть ключевые слова, а могут и не быть
        if not data['keywords']:
            # Добавляем данные в БД
            session.add_all(post)
        else:
            # Проверяем, есть ли ключевые слова в БД, если нет, то создаем их
            post_with_keywords = []
            for keyword_name in data['keywords']:
                keyword = session.query(models.Keyword).filter_by(
                    name=keyword_name).first()
                if not keyword:
                    keyword = models.Keyword(keyword_name)
                post_with_keyword = models.PostKeywordLink(keyword=keyword,
                                                           post=post)
                post_with_keywords.append(post_with_keyword)
            # Добавляем данные в БД
            session.add_all(post_with_keywords)
        session.commit()
