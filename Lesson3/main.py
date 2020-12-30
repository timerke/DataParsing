import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from database import Database


class GeekBrains_parser():
    """Класс для сбора данных о постах в GeekBrains."""

    # Заголовок запросов
    HEADERS = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 \
            Safari/537.36'}

    def __init__(self, url, db_name):
        """Конструктор класса.
        :param url: начальный url-адрес страницы с постами;
        :param db_name: имя базы данных, в которую будут сохраняться данные."""

        self.START_URL = url  # начальный адрес страниц с постами
        self._visited_urls = set()  # список url посещенных постов
        self.db = Database(db_name)

    def _get_next_page_url(self, soup):
        """Метод получает следующую страницу с постами.
        :param soup: bs4-объект с данными страницы с постами.
        :return: url-адрес следующей страницы с постами, если страниц больше
        нет, то возвращается None."""

        pagination = soup.find(attrs={'class': 'gb__pagination'})
        next_page = pagination.find(attrs={'class': 'active'}).next_sibling
        if not next_page:
            return None
        href = next_page.find('a')['href']
        return urljoin(self.START_URL, href)

    def _get_page(self, url):
        """Метод получает страницу с постами.
        :param url: url-адрес страницы."""

        r = requests.get(url, headers=self.HEADERS)
        if r.status_code != 200:
            return
        soup = bs(r.text, 'lxml')
        # Получаем url-адреса постов и получаем данные из постов
        for post_url in self._get_posts_urls(soup):
            data = self._get_post_data(post_url)
            self.db.save_data(data)
        return self._get_next_page_url(soup)

    def _get_posts_urls(self, soup):
        """Метод возвращает url-адрес поста.
        :param soup: bs4-объект с данными страницы с постами.
        :return: url-адрес поста."""

        post_items = soup.find_all('div', attrs={'class': 'post-item'})
        for post_item in post_items:
            url = urljoin(self.START_URL, post_item.find('a')['href'])
            if url in self._visited_urls:
                # Пост уже обработан
                continue
            # Пост еще не обработан
            self._visited_urls.add(url)
            yield url

    def _get_post_data(self, url):
        """Метод возвращает необходимые данные из поста.
        :param url: url-адрес поста.
        :return: словарь с данными поста."""

        r = requests.get(url, headers=self.HEADERS)
        if r.status_code != 200:
            return None
        soup = bs(r.text, 'lxml')
        # Заголовок поста
        title = soup.find('h1', attrs={'class': 'blogpost-title'})
        if title:
            title = title.string
        # Ссылка на картинку поста
        try:
            spam = soup.find('div', attrs={'class': 'blogpost-content'})
            picture = spam.find('img')['src']
        except:
            picture = None
        # Дата публикации
        try:
            spam = soup.find('div', attrs={'class': 'blogpost-date-views'})
            date = spam.find('time')['datetime']
        except:
            date = None
        # Автор
        try:
            author_div = soup.find('div', attrs={'itemprop': 'author'})
            author = author_div.string
            author_url = urljoin(self.START_URL,
                                 author_div.find_parent()['href'])
        except:
            author = None
            author_url = None
        # Ключевые слова
        try:
            keywords = soup.find(
                'i', attrs={'class': 'i-tag'}).get('keywords').split(', ')
        except:
            keywords = None
        # Комментарии
        comments = []
        for comment_div in soup.find_all('li', attrs={'class': 'gb__comment-item'}):
            print(comment_div)
            comment_author = comment_div.find(
                'a', attrs={'class': 'gb__comment-item-header-user-data-name'})
            comment_author_url = urljoin(
                self.START_URL, comment_author['href'])
            comment_author = comment_author.string
            comment_text = comment_div.find(
                'div', attrs={'class': 'gb__comment-item-body-content'})['text']
            comments.append({'author': comment_author,
                             'author_url': comment_author_url,
                             'text': comment_text})
        return {'post': {'url': url,
                         'title': title,
                         'picture': picture,
                         'date': date},
                'author': {'name': author,
                           'url': author_url},
                'keywords': keywords,
                'comments': comments}

    def run(self):
        """Метод запускает сбор данных о постах."""

        url = self.START_URL
        while url:
            url = self._get_page(url)
            print(url)


if __name__ == '__main__':
    URL = 'https://geekbrains.ru/posts/'
    DB_NAME = 'sqlite:///users.db'
    parser = GeekBrains_parser(URL, DB_NAME)
    parser.run()
