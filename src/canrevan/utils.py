import os
import random
import string
import asyncio
import functools
from datetime import datetime, timedelta
from typing import List, Iterable, Any, Callable


def notifiable(func):
    @functools.wraps(func)
    async def wrapper(*args, callback: Callable = None, **kwargs):
        try:
            result = await func(*args, **kwargs)
        finally:
            # If callback is given, then call callback function to notify that
            # the given function is finished.
            if callback is not None:
                callback()
        return result
    return wrapper


def drange(start: str, end: str, step: int = 1) -> List[str]:
    start_date = datetime.strptime(start, '%Y%m%d')
    end_date = datetime.strptime(end, '%Y%m%d')

    iters = (end_date - start_date).days // step
    return [(start_date + timedelta(days=d * step)).strftime('%Y%m%d')
            for d in range(iters + 1)]


def split_list(seq: List, chunks: int) -> List[List]:
    chunk_list = []
    chunk_size = len(seq) // chunks

    for i in range(chunks - 1):
        chunk_list.append(seq[i * chunk_size:(i + 1) * chunk_size])
    chunk_list.append(seq[(chunks - 1) * chunk_size:])

    return chunk_list


def random_filename(parent: str) -> str:
    return os.path.join(parent, ''.join(random.choices(
        string.digits + string.ascii_lowercase, k=16)))


def random_filenames(parent: str, n: int) -> List[str]:
    return [random_filename(parent) for _ in range(n)]


class Context(object):
    def __init__(self, max_tasks: int):
        self.max_tasks = max_tasks

    async def run(self, aws: Iterable) -> Any:
        tasks, results, errors = set(), [], 0
        for a in aws:
            if len(tasks) >= self.max_tasks:
                # If pool is full, wait for the first-completed task.
                done, tasks = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED)

                # Update results or exceptions.
                for d in done:
                    try:
                        r = d.result()
                        if r is not None:
                            results.append(r)
                    except Exception:
                        errors += 1

            # Add new task and put into the pool.
            tasks.add(asyncio.ensure_future(a))

        # After adding all tasks to the pool, wait for the rest tasks.
        done, _ = await asyncio.wait(tasks)

        # Update results or exceptions.
        for d in done:
            try:
                r = d.result()
                if r is not None:
                    results.append(r)
            except Exception:
                errors += 1

        return results, errors
