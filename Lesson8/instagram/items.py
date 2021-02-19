"""Модуль с моделью данных, которые будут сохранены в базу данных."""

import scrapy


class UserItem(scrapy.Item):
    """Модель с данными о пользователе Instagram."""

    # Id
    _id = scrapy.Field()
    # Логин пользователя
    username = scrapy.Field()
    # Полное имя пользователя
    full_name = scrapy.Field()
    # Id пользователя в Instagram
    user_instagram_id = scrapy.Field()
    # Дата парсинга
    date = scrapy.Field()


class SubscriptionItem(scrapy.Item):
    """Модель с данными о подписках."""

    # Id
    _id = scrapy.Field()
    # Id в Instagram пользователя-подписчика
    follower_id = scrapy.Field()
    # Id в Instagram пользователя, на которого подписан подписчик
    following_id = scrapy.Field()
