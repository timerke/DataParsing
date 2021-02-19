from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.exceptions import DropItem
from .database import Database
from .items import SubscriptionItem, UserItem
from .models import User


class DatabasePipeline:
    """Класс для записи данных о пользователях и о факте подписок в базу
    данных."""

    def __init__(self, db_name):
        """Конструктор.
        :param db_name: путь к базе данных."""

        self.db_name = db_name
    
    @classmethod
    def from_crawler(cls, crawler):

        db_settings = crawler.settings.getdict('DB_SETTINGS')
        if not db_settings:
            raise NotConfigured
        db_name = db_settings['db_name']
        return cls(db_name)

    def close_spider(self, spider):
        """Метод выполняется при закрытии паука. Закрываем соединение с базой
        данных."""

        pass

    def open_spider(self, spider):
        """Метод выполняется при запуске паука. Происходит соединение с базой
        данных."""

        self.db = Database(self.db_name)

    def process_item(self, item, spider):
        """Метод выполняет операции с Item, сохраняет данные в базу данных."""

        if isinstance(item, UserItem):
            # Записываем данные о пользователях
            user = User(item['username'], item['full_name'],
                        item['user_instagram_id'], item['date'])
            self.db.save_user(user)
        elif isinstance(item, SubscriptionItem):
            # Записываем данные о подписках
            self.db.save_subscription(item)
            # Записываем данные о взаимноподписанных
            self.db.save_handshake(item)
        return item
