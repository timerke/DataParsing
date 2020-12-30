"""Модуль содержит модели таблиц из базы данных."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship


Base = declarative_base()


class Author(Base):
    """Модель для таблицы с авторами постов."""

    __tablename__ = 'author'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return f'<Author({self.name}, {self.url})>'


class Post(Base):
    """Модель для таблицы с постами."""

    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship(Author, backref=backref('posts', uselist=True))
    keywords = relationship('Keyword', secondary='post_keyword_link')

    def __init__(self, url, title, picture, date, author):
        self.url = url
        self.title = title
        self.picture = picture
        self.date = date
        self.author = author

    def __repr__(self):
        return f'<Post({self.title}, {self.date})>'


class Keyword(Base):
    """Модель для таблицы с ключевыми словами."""

    __tablename__ = 'keyword'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    posts = relationship(Post, secondary='post_keyword_link')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Keyword({self.name})>'


class PostKeywordLink(Base):
    """Модель для осуществления связи многие-к-многим между моделями Post и
    Keyword."""

    __tablename__ = 'post_keyword_link'
    post_id = Column(Integer, ForeignKey('post.id'), primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keyword.id'), primary_key=True)
    post = relationship(Post, backref=backref('post_assoc'))
    keyword = relationship(Keyword, backref=backref('keyword_assoc'))


class Comment(Base):
    """Модель для таблицы с комментариями."""

    __tablename__ = 'comment'
    id = Column(Integer, autoincrement=True, primary_key=True)
    text = Column(String)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship(Author, backref=backref('comments', uselist=False))
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship(Post, backref=backref('posts', uselist=True))

    def __init__(self, text, author, post):
        self.text = text
        self.author = author
        self.post = post

    def __repr__(self):
        return f'<Keyword({self.author}, {self.text})>'
