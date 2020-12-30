"""Модуль для работы с базой данных."""

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Author, Base, Comment, Keyword, Post, PostKeywordLink


class Database():
    """Класс для работы с базой данных."""

    def __init__(self, db_name):
        """Конструктор класса.
        :param db_name: имя базы данных для подключения."""

        # Подключение к базе данных и создание таблиц
        engine = create_engine(db_name)
        Base.metadata.create_all(engine)
        # Создаем сессию
        self.Session = sessionmaker(bind=engine)

    def _create_comments(self, s, post, comments):
        """Метод создает список комментариев для добавления в БД.
        :param s: сессия работы с БД;
        :param post: пост, которому относятся создаваемые комментарии;
        :param comments: список комментариев.
        :return: список добавляемых комментариев в БД."""

        comments_in_post = []
        for comment_item in comments:
            # Проверяем, есть ли в БД автор коммента
            author_url = comment_item['author']['url']
            author = s.query(Author).filter_by(url=author_url).first()
            if not author:
                author = Author(**comment_item['author'])
            comment = Comment(comment_item['text'], author=author, post=post)
            comments_in_post.append(comment)
        return comments_in_post

    def _create_keywords(self, s, post, keywords):
        """Метод создает список ключевых слов для добавления в БД.
        :param s: сессия работы с БД;
        :param post: пост, которому относятся создаваемые ключевые слова;
        :param keywords: список ключевых слов поста.
        :return: список добавляемых ключевых слов в БД."""

        # Проверяем, есть ли ключевые слова в БД, если нет, то создаем
        post_with_keywords = []
        for keyword_name in keywords:
            keyword = s.query(Keyword).filter_by(name=keyword_name).first()
            if not keyword:
                keyword = Keyword(keyword_name)
            post_with_keyword = PostKeywordLink(keyword=keyword, post=post)
            post_with_keywords.append(post_with_keyword)
        return post_with_keywords

    def save_data(self, data):
        """Метод сохраняет данные в базу данных.
        :param data: данные для сохранения."""

        s = self.Session()
        # Проверяем, есть ли в БД автор, если нет, то создаем
        author_url = data['author']['url']
        author = s.query(Author).filter_by(url=author_url).first()
        if not author:
            author = Author(**data['author'])
        # Проверяем, есть ли в БД пост, если нет, то создаем
        post_url = data['post']['url']
        post = s.query(Post).filter_by(url=post_url).first()
        if post:
            # Пост в БД уже есть, дальше ничего не делаем
            return
        post = Post(**data['post'], author=author)
        s.add(post)
        # Если у поста есть ключевые слова, добавляем их в БД
        if data['keywords']:
            # Добавляем данные в БД
            keywords = self._create_keywords(s, post, data['keywords'])
            s.add_all(keywords)
        # Комментарии
        if data['comments']:
            comments = self._create_comments(s, post, data['comments'])
            s.add_all(comments)
        s.commit()
