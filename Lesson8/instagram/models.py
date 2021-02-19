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
    """Модель для таблицы с односторонними подписками: содержится информация,
    что пользователь с Id follower_id подписан на пользователя с Id
    following_id."""

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


class Handshake(Base):
    """Модель для таблицы с рукопожатиями: содержится информация, что
    пользователи с Id user_1_id и user_2_id подписаны друг на друга."""

    __tablename__ = 'handshake'
    id = Column(Integer, autoincrement=True, primary_key=True)
    # Ссылка на первого из взаимоподписанных пользователей
    user_1_id = Column(Integer, ForeignKey('user.id'))
    # Ссылка на второго из взаимоподписанных пользователей
    user_2_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, user_1, user_2):
        self.user_1_id = user_1.id
        self.user_2_id = user_2.id

    def __repr__(self):
        return f'<Handshake({self.user_1_id}, {self.user_2_id})>'
