import dotenv
import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instagram.spiders.instagram import InstagramSpider


if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule('instagram.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramSpider,
                          username=os.getenv('LOGIN'),
                          enc_password=os.getenv('PASSWORD'))
    crawler_process.start()
