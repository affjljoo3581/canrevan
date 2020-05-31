import os
import shutil
import argparse
from .crawling import start_crawling_articles


def _main():
    parser = argparse.ArgumentParser(
        prog='canrevan', description='crawl news article.')
    parser.add_argument('--output_file',
                        default='articles.txt',
                        help='output file path')
    parser.add_argument('--temporary',
                        default='tmp',
                        help='temporary directory path')
    parser.add_argument('--num_cores',
                        default=4,
                        type=int,
                        help='number of processes')
    parser.add_argument('--category',
                        required=True,
                        nargs='*',
                        type=int,
                        help='categories to crawl from')
    parser.add_argument('--start',
                        required=True,
                        help='start date string')
    parser.add_argument('--end',
                        required=True,
                        help='end date string')
    parser.add_argument('--step',
                        default=1,
                        type=int,
                        help='number of days to skip')
    parser.add_argument('--max_page',
                        default=100,
                        type=int,
                        help='maximum number of pages to search')
    args = parser.parse_args()

    # Create temporary directory.
    if not os.path.exists(args.temporary):
        os.makedirs(args.temporary)

    # Crawl news articles.
    start_crawling_articles(args.output_file,
                            args.temporary,
                            args.num_cores,
                            args.category,
                            args.start,
                            args.end,
                            args.step,
                            args.max_page)

    # Remove temporary directory.
    shutil.rmtree(args.temporary)
