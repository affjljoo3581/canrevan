import os
import re
import kss
import shutil
from . import utils
from multiprocessing import Process, Queue
from typing import Dict, Any


_re_special_symbols = re.compile(r'[\/|*^@\#▲▶◆◀■【】\\\=]')


def _clean_article_content(content: str) -> str:
    content = _re_special_symbols.sub(' ', content)
    content = content[content.find('다.') + 2:content.rfind('다.') + 2]
    return ' '.join(content.split())


def _clean_articles_worker(output_file: str, queue: Queue):
    with open(output_file, 'w', encoding='utf-8') as fp:
        while True:
            content = queue.get()

            # Terminate the process if queue returns `None`.
            if content is None:
                break

            # Write cleaned article content to output file.
            fp.write(_clean_article_content(content) + '\n')


def _tokenize_sentences_worker(input_file: str, output_file: str,
                               min_len: int):
    with open(input_file, 'r', encoding='utf-8') as src, \
            open(output_file, 'w', encoding='utf-8') as dst:
        for line in src:
            for s in kss.split_sentences(line):
                s = s.strip()
                if len(s) < min_len:
                    continue

                dst.write(s + '\n')


def _process_canrevan_article_contents(input_file: str,
                                       output_file: str,
                                       temporary: str,
                                       args: Dict[str, Any]):
    # Prepare cleaning articles in parallel.
    workers = []
    queue = Queue(maxsize=50 * args['num-cores'])
    cleaned_files = utils.random_filenames(temporary, args['num-cores'])

    # Start processes.
    for i in range(args['num-cores']):
        w = Process(target=_clean_articles_worker,
                    args=(cleaned_files[i], queue))
        w.daemon = True
        w.start()

        workers.append(w)

    # Read file and send to each process.
    with open(input_file, 'r', encoding='utf-8') as fp:
        for line in fp:
            queue.put(line)

    # Send terminate message to each process.
    for _ in range(args['num-cores']):
        queue.put(None)

    # Prepare tokenizing sentences in parallel.
    workers = []
    tokenized_files = utils.random_filenames(temporary, args['num-cores'])

    # Start processes.
    for i in range(args['num-cores']):
        w = Process(target=_tokenize_sentences_worker,
                    args=(cleaned_files[i],
                          tokenized_files[i],
                          args['min-length']))
        w.daemon = True
        w.start()

        workers.append(w)

    # Wait for terminating.
    for w in workers:
        w.join()

    # Remove temporary files.
    for name in cleaned_files:
        os.remove(name)

    # Merge temporary files into output file.
    with open(output_file, 'wb') as dst:
        for name in tokenized_files:
            with open(name, 'rb') as src:
                shutil.copyfileobj(src, dst)

    # Remove temporary files.
    for name in tokenized_files:
        os.remove(name)


__extension__ = {
    'name': 'canrevan extension',
    'version': '1.0',
    'description': 'clear crawled article contents.',
    'author': 'canrevan',
    'main': _process_canrevan_article_contents,
    'arguments': {
        'num-cores': {'type': int, 'default': 1},
        'min-length': {'type': int, 'default': 50}
    }
}
