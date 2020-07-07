import os
import re
import tqdm
import shutil
import asyncio
import aiohttp
import aiofiles
from . import utils
from bs4 import BeautifulSoup, SoupStrainer
from multiprocessing import Process, Queue
from typing import List


def _korean_characters_ratio(text: str) -> float:
    korean_characters = 0
    for c in text:
        if ord("가") <= ord(c) and ord(c) <= ord('힣'):
            korean_characters += 1
    return korean_characters / len(text)


async def _get_max_nav_pages(sess: aiohttp.ClientSession,
                             category: int,
                             date: str,
                             max_page: int = 100) -> int:
    nav_url = ('https://news.naver.com/main/list.nhn?mode=LSD&mid=shm'
               '&sid1={category}&date={date}&page={page}'
               .format(category=category, date=date, page=max_page))

    # Read navigation page and extract current page from container.
    async with sess.request('GET', nav_url) as resp:
        document = await resp.text()

    document = document[document.find('<div class="paging">'):]
    document = document[:document.find('</div>')]

    return int(re.search(r'<strong>(.*?)</strong>', document).group(1))


async def _get_article_urls_from_nav_page(sess: aiohttp.ClientSession,
                                          category: int,
                                          date: str,
                                          page: int) -> List[str]:
    nav_url = ('https://news.naver.com/main/list.nhn?mode=LSD&mid=shm'
               '&sid1={category}&date={date}&page={page}'
               .format(category=category, date=date, page=page))

    # Read navigation page and extract article links.
    async with sess.request('GET', nav_url) as resp:
        document = await resp.text()

    document = document[document.find('<ul class="type06_headline">'):]

    # Extract article url containers.
    list1 = document[:document.find('</ul>')]
    list2 = document[document.find('</ul>') + 5:]
    list2 = list2[:list2.find('</ul>')]

    document = list1 + list2

    # Extract all article urls from their containers.
    article_urls = []
    while '<dt>' in document:
        document = document[document.find('<dt>'):]
        container = document[:document.find('</dt>')]

        if not container.strip():
            continue

        article_urls.append(
            re.search(r'<a href="(.*?)"', container).group(1))

        document = document[document.find('</dt>'):]

    return article_urls


async def _get_article_content(sess: aiohttp.ClientSession,
                               article_url: str) -> str:
    # Use `SoupStrainer` to improve performance.
    async with sess.request('GET', article_url) as resp:
        document = await resp.text()

    strainer = SoupStrainer('div', attrs={'id': 'articleBodyContents'})
    document = BeautifulSoup(document, 'lxml', parse_only=strainer)
    content = document.find('div')

    # Skip if there is no article content in the page.
    if content is None:
        return ''

    # Remove unnecessary tags.
    for child in content.find_all():
        child.clear()

    return ' '.join(content.get_text().split())


def _collect_article_urls_worker(queue: Queue,
                                 category_list: List[str],
                                 date_list: List[str],
                                 max_page: int = 100,
                                 max_tasks: int = 50):
    async def main_fn():
        @utils.notifiable
        async def async_fn(sess, category, date):
            article_urls = []

            # Get maximum number of pages in navigation.
            pages = await _get_max_nav_pages(sess, category, date, max_page)

            # Collect all article urls from the given page index.
            for page in range(1, pages + 1):
                article_urls += await _get_article_urls_from_nav_page(
                    sess, category, date, page)

            return article_urls

        ctx = utils.Context(max_tasks=max_tasks)
        async with aiohttp.ClientSession() as sess:
            article_urls_stack, errors = await ctx.run((
                async_fn(sess, category, date,
                         callback=lambda: queue.put(None))
                for category in category_list
                for date in date_list))

        # Flatten the collected article urls and return it by putting to the
        # queue.
        queue.put(sum(article_urls_stack, []))

    # Execute async main function.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_fn())


def _crawl_articles_worker(queue: Queue,
                           output_file: str,
                           article_urls: List[str],
                           max_tasks: int = 50):
    async def main_fn():
        @utils.notifiable
        async def async_fn(sess, article_url, fp):
            # Get news article content and save it to the output file.
            content = await _get_article_content(sess, article_url)
            if _korean_characters_ratio(content) > 0.5:
                await fp.write(content + '\n')

        ctx = utils.Context(max_tasks=max_tasks)
        async with aiohttp.ClientSession() as sess:
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as fp:
                _, errors = await ctx.run((
                    async_fn(sess, article_url, fp,
                             callback=lambda: queue.put(True))
                    for article_url in article_urls))

        # Notify that current process is finished.
        queue.put(None)

    # Execute async main function.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_fn())


def start_crawling_articles(output_file: str,
                            temporary: str,
                            num_cores: int,
                            category_list: List[str],
                            start_date: str,
                            end_date: str,
                            date_step: int,
                            max_page: int = 100,
                            max_tasks: int = 50):
    date_list = utils.drange(start_date, end_date, date_step)
    total_search = len(date_list) * len(category_list)

    # Prepare multi-processing.
    workers = []
    queue = Queue()
    date_list_chunks = utils.split_list(date_list, chunks=num_cores)

    for i in range(num_cores):
        w = Process(target=_collect_article_urls_worker,
                    args=(queue,
                          category_list,
                          date_list_chunks[i],
                          max_page,
                          max_tasks))
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
                    args=(queue,
                          crawled_files[i],
                          article_list_chunks[i],
                          max_tasks))
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
