import re
import tempfile
from canrevan.crawling import Crawler

_dummy_urls = [f'https://news.naver.com/main/list.nhn?mode=LSD&mid=shm'
               f'&sid1=100&date=20200501&page={page}'
               for page in range(1, 3)]


def _get_current_page_from_html(content: str) -> int:
    content = content[content.find('<div class="paging">'):]
    content = content[:content.find('</div>')]

    return int(re.search(r'<strong>(.*?)</strong>', content).group(1))


def test_crawl_reduce_array():
    crawler = Crawler(concurrent_requests=500,
                      request_headers={'user-agent': 'canrevan'},
                      request_timeout=1)
    current_pages = crawler.reduce_to_array(
        _dummy_urls, parse_fn=_get_current_page_from_html)

    for page in current_pages:
        # Note that we only crawled up to 3 pages from each category and date.
        assert isinstance(page, int)
        assert page < 3


def test_crawl_reduce_file():
    crawler = Crawler(concurrent_requests=500,
                      request_headers={'user-agent': 'canrevan'},
                      request_timeout=1)

    with tempfile.TemporaryDirectory() as tdir:
        written = crawler.reduce_to_file(
            _dummy_urls,
            filename=f'{tdir}/crawled.txt',
            parse_fn=_get_current_page_from_html)

        # With a high probability, there must be successfully crawled data.
        assert written > 0

        with open(f'{tdir}/crawled.txt', 'r') as fp:
            for page in fp:
                page = int(page.strip())

                # Note that we only crawled up to 3 pages from each category
                # and date.
                assert page < 3
