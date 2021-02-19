import datetime
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from .items import SubscriptionItem, UserItem


def get_datetime(*args):
    """Функция получает время создания записи."""

    return datetime.datetime.now()


def get_data(data, name):
    """Функция получает значение некоторого поля из словаря.
    :param dict: словарь, из которого нужно получить значение;
    :param name: имя поля.
    :return: значение поля."""

    value = None
    if 'entry_data' in data:
        value = data['entry_data']['ProfilePage'][0]['graphql']['user'][name]
    elif 'node' in data:
        value = data['node'][name]
    return value


def get_follower_id(data):
    """Функция возвращает Id подписчика."""

    return data[0]['follower_id']


def get_following_id(data):
    """Функция возвращает Id пользователя, на которого кто-то подписан."""

    return data[0]['user_id']


def get_full_name(data):
    """Функция получает полное имя пользователя."""

    return get_data(data[0], 'full_name')


def get_user_instagram_id(data):
    """Функция получает Id пользователя из Instagram."""

    return get_data(data[0], 'id')


def get_username(data):
    """Функция получает логин пользователя."""

    return get_data(data[0], 'username')


class SubscriptionLoader(ItemLoader):

    default_item_class = SubscriptionItem
    follower_id_out = get_follower_id
    following_id_out = get_following_id


class UserLoader(ItemLoader):

    default_item_class = UserItem
    username_out = get_username
    full_name_out = get_full_name
    user_instagram_id_out = get_user_instagram_id
    date_out = get_datetime
