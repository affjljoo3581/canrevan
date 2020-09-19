import asyncio
from asyncio import Semaphore
from aiohttp import ClientSession, ClientTimeout
from concurrent.futures import ProcessPoolExecutor
from typing import List, Iterable, Dict, Callable, Optional, TypeVar

T = TypeVar('T')


class Crawler:
    def __init__(self,
                 concurrent_requests: int = 500,
                 num_parsing_processes: int = 1,
                 request_headers: Optional[Dict[str, str]] = None,
                 request_timeout: Optional[float] = None):
        self.concurrent_requests = concurrent_requests
        self.num_parsing_processes = num_parsing_processes
        self.request_headers = request_headers
        self.request_timeout = request_timeout

    async def _fetch_and_parse(self,
                               sem: Semaphore,
                               pool: ProcessPoolExecutor,
                               sess: ClientSession,
                               url: str,
                               parse_fn: Optional[Callable[[str], T]] = None
                               ) -> str:
        async with sem, sess.get(url) as resp:
            if parse_fn is None:
                return await resp.text()

            # Run `parse_fn` in subprocess from process-pool for parallelism.
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                pool, parse_fn, await resp.text())

    async def _crawl_and_reduce(
            self,
            urls: Iterable[str],
            parse_fn: Optional[Callable[[str], T]] = None,
            callback_fn: Optional[Callable[[T], None]] = None
            ):
        # Create a semaphore to limit the number of concurrent requests, a
        # process-pool executor to run `parse_fn` in parallel and a http client
        # session for asynchronous HTTP requests.
        sem = Semaphore(self.concurrent_requests)
        pool = ProcessPoolExecutor(max_workers=self.num_parsing_processes)
        sess = ClientSession(headers=self.request_headers,
                             timeout=ClientTimeout(total=self.request_timeout))

        # Create fetch tasks and add callback functions.
        futures = [asyncio.ensure_future(
                        self._fetch_and_parse(sem, pool, sess, url, parse_fn))
                   for url in urls]
        if callback_fn is not None:
            for f in futures:
                f.add_done_callback(
                    lambda f: callback_fn(f.exception() or f.result()))

        # Wait for the tasks to complete and close the http client session and
        # process-pool executor
        await asyncio.wait(futures)
        await sess.close()
        pool.shutdown(wait=True)

    def reduce_to_array(self,
                        urls: Iterable[str],
                        parse_fn: Optional[Callable[[str], T]] = None,
                        update_fn: Optional[Callable[[], None]] = None
                        ) -> List[T]:
        # A callback function to reduce collected data to the array.
        def callback_fn(data: T):
            if update_fn is not None:
                update_fn()

            if not isinstance(data, Exception):
                results.append(data)

        results = []
        asyncio.get_event_loop().run_until_complete(
            self._crawl_and_reduce(urls, parse_fn, callback_fn))

        return results

    def reduce_to_file(self,
                       urls: Iterable[str],
                       filename: str,
                       parse_fn: Optional[Callable[[str], T]] = None,
                       update_fn: Optional[Callable[[], None]] = None) -> int:
        with open(filename, 'w') as fp:
            # A callback function to reduce collected data to the output file.
            def callback_fn(data: T):
                if update_fn is not None:
                    update_fn()

                if not isinstance(data, Exception):
                    # Increase the counter which indicates the number of actual
                    # reduced items.
                    nonlocal written
                    written += 1

                    fp.write(str(data) + '\n')

            written = 0
            asyncio.get_event_loop().run_until_complete(
                self._crawl_and_reduce(urls, parse_fn, callback_fn))

        return written
