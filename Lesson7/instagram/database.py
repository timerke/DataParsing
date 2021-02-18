"""Модуль для работы с базой данных."""

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Subscription, User


class Database():
    """Класс для работы с базой данных."""

    def __init__(self, db_name):
        """Конструктор класса.
        :param db_name: имя базы данных для подключения."""

        # Подключение к базе данных и создание таблиц
        engine = create_engine(db_name)
        Base.metadata.create_all(engine)
        # Создаем сессию
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def __del__(self):
        """Деструктор."""

        #self.session.close()
        self.session.close()

    def save_subscription(self, data):
        """Метод сохраняет данные о подписках пользователей.
        :param data: данные для сохранения."""

        # Находим пользователя-подписчика
        follower = self.session.query(User).filter_by(
            user_instagram_id=data['follower_id']).first()
        # Находим пользователя, на которого подписан подписчик
        following = self.session.query(User).filter_by(
            user_instagram_id=data['following_id']).first()
        # Проверяем, что этой подписки пока нет в базе данных
        subscription = self.session.query(Subscription).filter_by(
            follower_id=follower.id, following_id=following.id).first()
        if subscription:
            # Подписка уже записана в базу данных
            return
        # Подписки в базе данных нет.        
        # Создаем подписку и записываем в базу данных
        subscription = Subscription(follower, following)
        self.session.add(subscription)
        self.session.commit()

    def save_user(self, user):
        """Метод сохраняет данные о пользователе в базу данных.
        :param user: данные для сохранения."""

        # Проверяем, есть ли уже в базе данных пользователь
        existing_user = self.session.query(User).filter_by(
                        user_instagram_id=user.user_instagram_id).first()
        if not existing_user:
            # Пользователь еще не записан, запишем его в базу
            self.session.add(user)
            self.session.commit()
