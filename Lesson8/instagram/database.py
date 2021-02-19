"""Модуль для работы с базой данных."""

import datetime
import queue
from sqlalchemy import and_, create_engine, or_
from sqlalchemy.orm import sessionmaker
from .models import Base, Handshake, Subscription, User


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

        self.session.close()

    def find_handshakes(self, username_1, username_2):
        """Метод ищет цепочку рукопожатий между исследуемыми пользователями.
        Применяем метод поиска в ширину."""

        user_1 = self.session.query(User).filter_by(
            username=username_1).first()
        user_2 = self.session.query(User).filter_by(
            username=username_2).first()
        if not user_1 or not user_2:
            # Один или оба исследуемых пользователя не найдены
            return
        # Помещаем первого пользователя в очередь
        q = queue.Queue()
        q.put(user_1)
        # Формируем множество для пройденных пользователей
        used_friends = set(username_1)
        # Дерево связей между пользователями
        tree = {username_1: None}
        searched = False
        while not q.empty() and not searched:
            # Извлекаем пользователя, первым стоящим в очереди
            user = q.get()
            used_friends.add(user.username)
            # Ищем знакомых пользователя
            friends = self.session.query(User).filter(
                or_(Handshake.user_1_id == user.id,
                    Handshake.user_2_id == user.id))
            for friend in friends:
                if friend == username_2:
                    # Мы нашли путь до второго пользователя
                    searched = True
                    tree[username_2] = user.username
                    used_friends.add(username_2)
                    break
                if friend.username not in used_friends:
                    # Помещаем найденных знакомых, которые еще не изучены,
                    # в очередь
                    q.put(friend)
                    # Помещаем в дерево
                    tree[friend.username] = user.username
                    used_friends.add(friend.username)
        # Выводим путь рукопожатий между пользователями
        if not tree.get(username_2):
            print(f'Не найдена цепочка рукопожатий между {username_1} и '
                  f'{username_2}!')
            return
        print(f'Цепочка рукопожатий между {username_1} и {username_2}:')
        username = username_2
        while tree.get(username_2):
            print(f'{username} -> ', end='')

    def save_handshake(self, data):
        """Метод сохраняет данные о рукопожатиях (взаимоподписанных
        пользователях).
        :param data: данные для сохранения."""

        # Находим пользователей
        user_1 = self.session.query(User).filter_by(
            user_instagram_id=data['follower_id']).first()
        user_2 = self.session.query(User).filter_by(
            user_instagram_id=data['following_id']).first()
        # Проверяем, что они взаимноподписаны
        subs = self.session.query(Subscription).filter(
            or_(
                and_(Subscription.follower_id == user_1.id,
                     Subscription.following_id == user_2.id),
                and_(Subscription.follower_id == user_2.id,
                     Subscription.following_id == user_1.id))).count()
        if subs < 2:
            # Пользователя не являются взаимноподписанными
            return
        # Пользователи взаимноподписаны, потому проверяем, есть ли они в
        # таблице взаимноподписанных
        handshake = self.session.query(Handshake).filter(
            or_(
                and_(Handshake.user_1_id == user_1.id,
                     Handshake.user_2_id == user_2.id),
                and_(Handshake.user_1_id == user_2.id,
                     Handshake.user_2_id == user_1.id))).count()
        if handshake:
            # Пользователи уже записаны в таблицу взаимноподписанных
            return
        handshake = Handshake(user_1, user_2)
        self.session.add(user_1, user_2)
        self.session.commit()

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
