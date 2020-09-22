import ssl
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta
from typing import List, Dict


def drange(start: str, end: str, step: int = 1) -> List[str]:
    start_date = datetime.strptime(start, '%Y%m%d')
    end_date = datetime.strptime(end, '%Y%m%d')

    iters = (end_date - start_date).days // step
    return [(start_date + timedelta(days=d * step)).strftime('%Y%m%d')
            for d in range(iters + 1)]


def korean_character_ratio(text: str, ignore_whitespace: bool = True) -> float:
    if ignore_whitespace:
        text = ''.join(text.split())

    korean_characters = len([
        c for c in text if ord('가') <= ord(c) <= ord('힣')])
    return korean_characters / len(text)


def is_normal_character(c: str) -> bool:
    return (ord('0') <= ord(c) <= ord('9')
            or ord('a') <= ord(c) <= ord('z')
            or ord('A') <= ord(c) <= ord('Z')
            or ord('가') <= ord(c) <= ord('힣'))


def ignore_aiohttp_ssl_error(loop: AbstractEventLoop):
    original_handler = loop.get_exception_handler()

    def ignore_ssl_error(loop: AbstractEventLoop, context: Dict):
        # Ignore SSLError from `aiohttp` module. It is known as a bug.
        if isinstance(context['exception'], ssl.SSLError):
            return

        if original_handler is not None:
            original_handler(loop, context)
        else:
            loop.default_exception_handler(context)

    loop.set_exception_handler(ignore_ssl_error)
