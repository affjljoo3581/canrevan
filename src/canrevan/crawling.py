import asyncio
import warnings
from asyncio import Semaphore
import canrevan.utils as utils
from aiohttp import ClientSession, ClientTimeout
from concurrent.futures import Executor, ProcessPoolExecutor
from typing import List, Iterable, Dict, Callable, Optional, TypeVar

# Ignore warnings from `aiohttp` module.
warnings.filterwarnings('ignore', module='aiohttp')

T = TypeVar('T')


class Crawler:
    def __init__(self,
                 concurrent_tasks: int = 500,
                 num_parsing_processes: int = 1,
                 request_headers: Optional[Dict[str, str]] = None,
                 request_timeout: Optional[float] = None):
        self.concurrent_tasks = concurrent_tasks
        self.num_parsing_processes = num_parsing_processes
        self.request_headers = request_headers
        self.request_timeout = request_timeout

    async def _fetch_and_parse(self,
                               sem: Semaphore,
                               pool: Executor,
                               sess: ClientSession,
                               url: str,
                               parse_fn: Optional[Callable[[str], T]] = None
                               ) -> Optional[str]:
        try:
            async with sess.get(url) as resp:
                content = await resp.text()

            # Run `parse_fn` in subprocess from process-pool for parallelism.
            if parse_fn is not None:
                content = await asyncio.get_event_loop().run_in_executor(
                    pool, parse_fn, content)
        except Exception:
            content = None

        sem.release()
        return content

    async def _crawl_and_reduce(
            self,
            urls: Iterable[str],
            parse_fn: Optional[Callable[[str], T]] = None,
            callback_fn: Optional[Callable[[Optional[T]], None]] = None):
        # Create a semaphore to limit the number of concurrent tasks, a
        # process-pool executor to run `parse_fn` in parallel and a http client
        # session for asynchronous HTTP requests.
        sem = Semaphore(self.concurrent_tasks)
        pool = ProcessPoolExecutor(max_workers=self.num_parsing_processes)
        sess = ClientSession(headers=self.request_headers,
                             timeout=ClientTimeout(total=self.request_timeout))

        futures = []
        for url in urls:
            await sem.acquire()

            # Create a fetching future.
            f = asyncio.ensure_future(
                self._fetch_and_parse(sem, pool, sess, url, parse_fn))

            # Add done-callback function to the future.
            if callback_fn is not None:
                f.add_done_callback(lambda f: callback_fn(f.result()))

            futures.append(f)

        # Wait for the tasks to be complete and close the http client session
        # and process-pool executor
        await asyncio.wait(futures)
        await sess.close()
        pool.shutdown(wait=True)

    def reduce_to_array(self,
                        urls: Iterable[str],
                        parse_fn: Optional[Callable[[str], T]] = None,
                        update_fn: Optional[Callable[[], None]] = None
                        ) -> List[T]:
        # A callback function to reduce collected data to the array.
        def callback_fn(data: Optional[T]):
            if update_fn is not None:
                update_fn()

            if data is not None:
                results.append(data)

        # Get event loop and set to ignore `SSLError`s from `aiohttp` module.
        loop = asyncio.get_event_loop()
        utils.ignore_aiohttp_ssl_error(loop)

        results = []
        loop.run_until_complete(
            self._crawl_and_reduce(urls, parse_fn, callback_fn))

        return results

    def reduce_to_file(self,
                       urls: Iterable[str],
                       filename: str,
                       parse_fn: Optional[Callable[[str], T]] = None,
                       update_fn: Optional[Callable[[], None]] = None) -> int:
        with open(filename, 'w') as fp:
            # A callback function to reduce collected data to the output file.
            def callback_fn(data: Optional[T]):
                if update_fn is not None:
                    update_fn()

                if data is not None:
                    # Increase the counter which indicates the number of actual
                    # reduced items.
                    nonlocal written
                    written += 1

                    fp.write(str(data) + '\n')

            # Get event loop and set to ignore `SSLError`s from `aiohttp`
            # module.
            loop = asyncio.get_event_loop()
            utils.ignore_aiohttp_ssl_error(loop)

            written = 0
            loop.run_until_complete(
                self._crawl_and_reduce(urls, parse_fn, callback_fn))

        return written
