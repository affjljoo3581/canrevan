import os
import tqdm
import shutil
from . import utils
from urllib.request import urlopen
from bs4 import BeautifulSoup, SoupStrainer
from multiprocessing import Process, Queue
from typing import List


_NAV_ARTICLES_URL = ('http://news.naver.com/main/list.nhn?mode=LSD&mid=shm'
                     '&sid1={category}&date={date}&page={page}')


def _get_max_nav_pages(category: int,
                       date: str,
                       max_page: int = 100) -> int:
    nav_url = _NAV_ARTICLES_URL.format(category=category,
                                       date=date,
                                       page=max_page)

    # Read navigation page.
    with urlopen(nav_url) as res:
        # Use `SoupStrainer` to improve performance.
        strainer = SoupStrainer('div', {'class': 'paging'})
        document = BeautifulSoup(res.read(), 'lxml', parse_only=strainer)
        max_page_elem = document.find('strong')

    return int(max_page_elem.get_text())


def _get_article_urls_from_nav_page(category: int,
                                    date: str,
                                    page: int) -> List[str]:
    nav_url = _NAV_ARTICLES_URL.format(category=category,
                                       date=date,
                                       page=page)

    # Read navigation page and extract article links.
    with urlopen(nav_url) as res:
        # Use `SoupStrainer` to improve performance.
        strainer = SoupStrainer('div', {'class': 'list_body newsflash_body'})
        document = BeautifulSoup(res.read(), 'lxml', parse_only=strainer)

        article_items = document.find_all('li')
        article_urls = [item.find('a').get('href') for item in article_items]

    return article_urls


def _get_article_content(article_url: str) -> str:
    with urlopen(article_url) as res:
        # Use `SoupStrainer` to improve performance.
        strainer = SoupStrainer('div', attrs={'id': 'articleBodyContents'})
        document = BeautifulSoup(res.read(), 'lxml', parse_only=strainer)
        content = document.find('div')

        # Skip if there is no article content in the page.
        if content is None:
            return ''

        # Remove unnecessary tags.
        for child in content.find_all():
            child.clear()

        article_content = ' '.join(content.get_text().split())

    return article_content


def _collect_article_urls_worker(queue: Queue,
                                 category_list: List[str],
                                 date_list: List[str],
                                 max_page: int = 100):
    article_urls = []
    for category in category_list:
        for date in date_list:
            # Get maximum number of pages in navigation.
            pages = _get_max_nav_pages(category, date, max_page)

            for page in range(1, pages + 1):
                article_urls += _get_article_urls_from_nav_page(category,
                                                                date,
                                                                page)
            queue.put(None)
    queue.put(article_urls)


def _crawl_articles_worker(output_file: str,
                           article_urls: List[str],
                           queue: Queue):
    with open(output_file, 'w', encoding='utf-8') as fp:
        for article_url in article_urls:
            fp.write(_get_article_content(article_url) + '\n')
            queue.put(True)
    queue.put(None)


def start_crawling_articles(output_file: str,
                            temporary: str,
                            num_cores: int,
                            category_list: List[str],
                            start_date: str,
                            end_date: str,
                            date_step: int,
                            max_page: int = 100):
    """Crawl news articles in parallel.

    Arguments:
        output_file (str): Output file path.
        temporary (str): Temporary directory path.
        num_cores (int): The number of processes.
        category_list (list): The list of categories to crawl from.
        start_date (str): Start date string.
        end_date (str): End date string.
        date_step (int): The number of days to skip.
        max_page (int): The maximum pages to crawl.
    """
    date_list = utils.drange(start_date, end_date, date_step)
    total_search = len(date_list) * len(category_list)

    # Prepare multi-processing.
    workers = []
    queue = Queue()
    date_list_chunks = utils.split_list(date_list, chunks=num_cores)

    for i in range(num_cores):
        w = Process(target=_collect_article_urls_worker,
                    args=(queue, category_list, date_list_chunks[i], max_page))
        w.daemon = True
        w.start()

        workers.append(w)

    # Gather article urls from processes.
    article_urls = []
    exit_processes = 0
    tqdm_iter = tqdm.trange(total_search, desc='[*] collect article urls')
    while True:
        batch_article_urls = queue.get()

        if batch_article_urls is None:
            tqdm_iter.update()
        else:
            article_urls += batch_article_urls
            exit_processes += 1

        # Exit for waiting processes.
        if exit_processes == num_cores:
            break
    tqdm_iter.close()

    print(f'[*] successfully collecting article urls.'
          f' total articles: {len(article_urls)}')

    # Prepare multi-processing.
    workers = []
    queue = Queue()

    # Create temporary files and split articles into chunks.
    crawled_files = utils.random_filenames(temporary, num_cores)
    article_list_chunks = utils.split_list(article_urls, chunks=num_cores)

    for i in range(num_cores):
        w = Process(target=_crawl_articles_worker,
                    args=(crawled_files[i], article_list_chunks[i], queue))
        w.daemon = True
        w.start()

        workers.append(w)

    # Show crawling progress.
    exit_processes = 0
    for _ in tqdm.trange(len(article_urls), desc='[*] crawl articles'):
        if queue.get() is None:
            exit_processes += 1

        # Exit for waiting processes.
        if exit_processes == num_cores:
            break

    # Merge temporary files into `output_file`.
    print(f'[*] finish crawling articles. merge chunks into [{output_file}].')
    with open(output_file, 'wb') as dst:
        for name in crawled_files:
            with open(name, 'rb') as src:
                shutil.copyfileobj(src, dst)

    # Remove temporary files.
    for name in crawled_files:
        os.remove(name)
