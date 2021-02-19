"""Пояснение, как работает паук.
Пауку нужно задать исходного пользователя. Паук найдет всех подписчиков
данного пользователя. Затем найдет всех подписчиков подписчиков и т.д. В итоге
будет собрана база данных из пользователей, которые подписаны хотя бы на одного
другого пользователя. В pipeline найдем пользователей, которые подписаны друг
на друга и получим таблицу с рукопожатиями: таблицу пользователей, которые
подписаны друг на друга и могут участвовать в цепочке рукопожатий. После этого
останется проанализировать таблицы знакомых друг с другом пользователей и найти
цепочку от исходного пользователя до конечного пользователя (который пока не
фигурировал в исследовании). Делаем это с помощью алгоритма поиска в ширину."""

import dotenv
import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instagram.spiders.instagram import InstagramSpider
from instagram.database import Database


if __name__ == '__main__':

    dotenv.load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule('instagram.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    # Логины пользователей, цепочку рукопожатий между которыми нужно найти
    start_user = 'vgree'
    final_user = 'karenjoke'
    # Задаем агументы поиска для паука и запускаем поиск
    crawler_process.crawl(InstagramSpider,
                          username=os.getenv('LOGIN'),
                          enc_password=os.getenv('PASSWORD'),
                          start_user='yanna_lev')
    crawler_process.start()
    # Поиск всех пользователей завершен, анализируем базу данных пользователей
    # и ищем кратчайшую цепочку.
    # Настраиваем базу данных
    db_settings = crawler_settings.getdict('DB_SETTINGS')
    if not db_settings:
        raise NotConfigured
    db_name = db_settings['db_name']
    db = Database(db_name)
    # Запускаем поиск цепочки рукопожатий
    db.find_handshakes(start_user, final_user)
