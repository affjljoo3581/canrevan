from datetime import datetime, timedelta
from typing import List


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
