from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import pymongo


class MongoPipeline:
    def __init__(self):
        self.db = pymongo.MongoClient()["instagram"]

    def process_item(self, item, spider):
        if not self.db[item.__class__.__name__].count({'url': item['url']}):
            self.db[item.__class__.__name__].insert_one(item)
        return item


class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if not item['data']['is_video']:
            # Скачиваем только картинки
            img_url = item.get('url')
            yield Request(img_url)

    def item_completed(self, results, item, info):
        i = results[0][1]
        i.pop('url', None)
        item['image'] = i
        return item
