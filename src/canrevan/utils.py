import os
import random
import string
from datetime import datetime, timedelta
from typing import List


_CANDIDATES = string.digits + string.ascii_lowercase


def drange(start: str, end: str, step: int = 1) -> List[str]:
    """Return dates between ``start`` and ``end``.

    Arguments:
        start (str): Start date string.
        end (str): End date string.

    Note:
        Each date string must be in `yyyyMMdd` format.

    Returns:
        A list of date strings.
    """
    start_date = datetime.strptime(start, '%Y%m%d')
    end_date = datetime.strptime(end, '%Y%m%d')

    iters = (end_date - start_date).days // step
    return [(start_date + timedelta(days=d * step)).strftime('%Y%m%d')
            for d in range(iters + 1)]


def split_list(seq: List, chunks: int):
    """Split list into chunks.

    Arguments:
        seq (list): The list to split.
        chunks (int): The number of chunks.

    Returns:
        A list of chunks which are from input list.
    """
    chunk_list = []
    chunk_size = len(seq) // chunks

    for i in range(chunks - 1):
        chunk_list.append(seq[i * chunk_size:(i + 1) * chunk_size])
    chunk_list.append(seq[(chunks - 1) * chunk_size:])

    return chunk_list


def random_filename(parent: str) -> str:
    r"""Generate random filename consists of 16 characters.

    Arguments:
        parent (str): Parent directory for file.

    Returns:
        Randomly generated file name.
    """
    return os.path.join(parent, ''.join(random.choices(_CANDIDATES, k=16)))


def random_filenames(parent: str, n: int) -> List[str]:
    r"""Generate multiple random filenames.

    Arguments:
        parent (str): Parent directory for files.
        n (int): Total number of filenames.

    Returns:
        Randomly generated file names.
    """
    return [random_filename(parent) for _ in range(n)]
