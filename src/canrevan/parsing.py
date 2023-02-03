import json
import re
from typing import List

from bs4 import BeautifulSoup, SoupStrainer

import utils as utils


def extract_article_urls(document: str, _: bool) -> List[str]:
    document = document[document.find('<ul class="type06_headline">'):]

    # Extract article url containers.
    list1 = document[: document.find("</ul>")]
    list2 = document[document.find("</ul>") + 5:]
    list2 = list2[: list2.find("</ul>")]

    document = list1 + list2

    # Extract all article urls from the containers.
    article_urls = []
    while "<dt>" in document:
        document = document[document.find("<dt>"):]
        container = document[: document.find("</dt>")]

        if not container.strip():
            continue

        article_urls.append(re.search(r'<a href="(.*?)"', container).group(1))
        document = document[document.find("</dt>"):]

    return article_urls


def parse_article_content(document: str, include_reporter_name: bool) -> str:
    strainer = SoupStrainer("div", attrs={"id": "dic_area"})
    document = BeautifulSoup(document, "lxml", parse_only=strainer)
    content = document.find("div")

    # Skip invalid articles which do not contain news contents.
    if content is None:
        raise ValueError("there is no any news article content.")

    # Remove unnecessary tags except `<br>` elements for preserving line-break
    # characters.
    for child in content.find_all():
        if child.name != "br":
            child.clear()

    content = content.get_text(separator="\n").strip()
    content = "\n".join([line.strip() for line in content.split('\n')])

    # Skip the contents which contain too many non-Korean characters.
    if utils.korean_character_ratio(content) < 0.5:
        raise ValueError("there are too few Korean characters in the content.")

    # Normalize the contents by removing abnormal sentences.
    content = "\n".join(
        [
            line
            for line in content.splitlines()
            if line[-1] == "."
        ]
    )

    # Remove reporter name part if set.
    if not include_reporter_name:
        splitted = content.split(sep='\n')
        content = "\n".join(splitted[1:])
        content = utils.remove_reporter_name(splitted[0]) + content

    # Remove empty string
    if content == "":
        raise ValueError("there is no news article content.")

    return json.encoder.encode_basestring(content)
