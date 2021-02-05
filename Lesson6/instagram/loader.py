import time
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from .items import InstagramItem


def get_datetime(*args):
    """Функция получает время создания записи."""

    return time.strftime('%Y-%m-%d %H:%M:%S')


def get_url(data):
    """Функция получает ссылку на картинку."""

    return data[0]['display_url']


class InstagramLoader(ItemLoader):

    default_item_class = InstagramItem
    data_out = TakeFirst()
    date_out = get_datetime
    url_out = get_url
