from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from vacancy import settings
from vacancy.spiders.hhru import HhruSpider


if __name__ == '__main__':
	crawler_settings = Settings()
	crawler_settings.setmodule(settings)
	process = CrawlerProcess(settings=crawler_settings)
	process.crawl(HhruSpider)
	process.start()