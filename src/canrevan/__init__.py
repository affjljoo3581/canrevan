import argparse
from typing import List

import tqdm

import parsing as parsing
import utils as utils
from crawling import Crawler

DEFAULT_USER_AGENT_STRING = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/87.0.4280.66 "
    "Safari/537.36"
)


def _main():
    args = _create_argument_parser().parse_args()

    # Create a crawler for collecting article urls and news contents.
    crawler = Crawler(
        concurrent_tasks=args.max_jobs,
        num_parsing_processes=args.num_cores,
        request_headers={"user-agent": args.user_agent},
        request_timeout=args.timeout,
    )

    # Collect article urls from navigation pages.
    nav_urls = _prepare_nav_urls(args)
    print(f"[*] navigation pages: {len(nav_urls)}")

    with tqdm.tqdm(nav_urls, desc="[*] collect article urls") as tbar:
        article_urls = crawler.reduce_to_array(
            nav_urls, args.include_reporter_name, parse_fn=parsing.extract_article_urls, update_fn=tbar.update
        )

    # Flatten the grouped urls and remove duplicates from the array.
    article_urls = {url for urls in article_urls for url in urls}
    print(f"[*] total collected articles: {len(article_urls)}")

    # Crawl news articles from the collected article urls and save the content to the
    # output file.
    with tqdm.tqdm(article_urls, desc="[*] crawl news article contents") as tbar:
        total_contents = crawler.reduce_to_file(
            article_urls,
            args.output_path,
            args.include_reporter_name,
            parse_fn=parsing.parse_article_content,
            update_fn=tbar.update,
        )

    print(
        f"[*] finish crawling {total_contents} news articles to "
        f"[{args.output_path}]"
    )


def _prepare_nav_urls(args: argparse.Namespace) -> List[str]:
    return [
        f"https://news.naver.com/main/list.nhn?mode=LSD&mid=shm"
        f"&sid1={category}&date={date}&page={page}"
        for category in args.category
        for date in utils.drange(args.start_date, args.end_date, args.skip_days)
        for page in range(1, args.max_page + 1)
    ]


def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="canrevan", description="crawl naver news articles"
    )

    parser.add_argument(
        "--output_path", default="첫줄포함.txt", help="output file path"
    )
    parser.add_argument(
        "--category",
        required=True,
        nargs="*",
        type=int,
        help="list of news article categories",
    )
    parser.add_argument(
        "--start_date", required=True, help="minimum date of news articles"
    )
    parser.add_argument(
        "--end_date", required=True, help="maximum date of news articles"
    )
    parser.add_argument(
        "--skip_days", default=1, type=int, help="number of days to skip from crawling"
    )
    parser.add_argument(
        "--max_page", default=10, type=int, help="maximum number of pages to navigate"
    )
    parser.add_argument(
        "--timeout", default=5, type=float, help="timeout for the whole request"
    )
    parser.add_argument(
        "--max_jobs",
        default=500,
        type=int,
        help="maximum number of concurrent requests",
    )
    parser.add_argument(
        "--num_cores",
        default=4,
        type=int,
        help="number of multi-processing cores for parsing",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT_STRING,
        help="use custom user-agent string",
    )
    parser.add_argument(
        "--include_reporter_name",
        default=False,
        help="",
    )

    return parser
