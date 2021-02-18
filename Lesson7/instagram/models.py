"""Модуль содержит модели таблиц из базы данных."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    """Модель для таблицы с пользователями."""

    __tablename__ = 'user'
    id = Column(Integer, autoincrement=True, primary_key=True)
    # Логин пользователя
    username = Column(String, nullable=False, unique=True)
    # Полное имя пользователя
    full_name = Column(String, nullable=False)
    # Id пользователя в Instagram
    user_instagram_id = Column(String, nullable=False, unique=True)
    # Дата парсинга
    date = Column(DateTime, nullable=False)

    def __init__(self, username, full_name, user_instagram_id, date):
        self.username = username
        self.full_name = full_name
        self.user_instagram_id = user_instagram_id
        self.date = date

    def __repr__(self):
        return f'<User({self.username}, {self.full_name}, {self.user_instagram_id})>'


class Subscription(Base):
    """Модель для таблицы с подписками."""

    __tablename__ = 'subscription'
    id = Column(Integer, autoincrement=True, primary_key=True)
    # Ссылка на пользователя-подписчика
    follower_id = Column(Integer, ForeignKey('user.id'))
    # Ссылка на пользователя, на которого подписан подписчик
    following_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, follower, following):
        self.follower_id = follower.id
        self.following_id = following.id

    def __repr__(self):
        return f'<Subscription({self.follower_id}, {self.following_id})>'
