# canrevan

[![PyPI version](https://badge.fury.io/py/canrevan.svg)](https://badge.fury.io/py/canrevan)
![build](https://github.com/affjljoo3581/canrevan/workflows/build/badge.svg)
[![GitHub license](https://img.shields.io/github/license/affjljoo3581/canrevan)](https://github.com/affjljoo3581/canrevan/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/affjljoo3581/canrevan/branch/master/graph/badge.svg)](https://codecov.io/gh/affjljoo3581/canrevan)
[![CodeFactor](https://www.codefactor.io/repository/github/affjljoo3581/canrevan/badge)](https://www.codefactor.io/repository/github/affjljoo3581/canrevan)

## Introduction
`canrevan`은 대량의 네이버 뉴스 기사를 수집하는 라이브러리입니다. 간단하게 한국어 뉴스
데이터셋을 구성하도록 도와줍니다.

NLP task에서 가장 중요한 부분 중 하나는 데이터셋입니다. 특히 한국어의 경우, 영어에 비해
수집할 수 있는 데이터가 매우 부족합니다. 특히, [위키피디아](https://ko.wikipedia.org/wiki/%EC%9C%84%ED%82%A4%EB%B0%B1%EA%B3%BC)
덤프 파일의 경우 영문 버전이 16.1GB인 것에 비해 한국어 버전은 651.3MB밖에 되지 않습니다.
그렇기 때문에, 일반적인 NLP 학습에 있어서 위키피디아와 같은 데이터셋을 사용하기에는 턱없이
부족합니다. 그렇다면 데이터셋 규모를 키우기 위해서 어떻게 해야 할까요? 우리는 다른 곳에서
데이터를 수집해야 합니다. 대표적으로 **뉴스 기사**가 있습니다.

실제로 많은 연구자들이 위키 데이터를 포함하여, 인터넷 뉴스 기사를 함께 사용해 말뭉치를
구성합니다. 인터넷 뉴스 기사는 다음과 같은 특징을 가지고 있습니다.

* 매우 많은 데이터를 가지고 있습니다. 매일 다양한 언론사에서 작성되는 기사의 양은 상당히
많습니다.
* 데이터의 품질이 우수합니다. 기본적으로 뉴스 기사는 맞춤법 뿐만 아니라 내용상으로 잘
구성되어 있습니다.
* 비교적 잘 정형화되어 있습니다. 인터넷 뉴스 기사는 암묵적으로 일정한 규칙과 구조를 가지고
있습니다. 정규화하기 쉽습니다.
* 다양한 분야의 문서가 존재합니다. 뉴스 기사는 분야와 주제를 가리지 않습니다. 정치, 사회,
경제 등등의 주제를 다룹니다.

[네이버 뉴스](https://news.naver.com/)는 각 언론사의 뉴스를 종합하여 제공합니다. 하나의
플랫폼에서 다양한 언론사의 방대한 뉴스 기사를 수집할 수 있습니다. 실제로 많은 연구자들이
네이버 뉴스를 통해 기사를 수집합니다.

`canrevan`은 네이버 뉴스에서 기사를 수집하도록 도와줍니다. 명령창에서 한 줄로 수
기가바이트의 데이터를 손쉽게 수집할 수 있습니다. 자세한 내용은 [여기](#Example)를
참고하시기 바랍니다.

## Dependencies
* tqdm>=4.46.0
* bs4
* lxml>=4.5.1
* aiohttp
* langumo

## Installation
### With pip
PyPI에서 canrevan을 설치할 수 있습니다. 자세한 명령어는 다음과 같습니다.
```console
$ pip install canrevan
```

### From source
혹은, 원격 저장소에서 복제하여 소스코드에서 직접 설치할 수 있습니다.
```console
$ git clone https://github.com/affjljoo3581/canrevan.git
$ cd canrevan
$ python setup.py install
```

## Example
수집하고자 하는 카테고리의 id를 [네이버 뉴스](https://news.naver.com/)에서 확인합니다. 본 예제에서는 정치(100)와 경제(101) 카테고리에 대한 뉴스를 수집해봅시다. 다음은 2020년 5월 1일부터 31일까지 5개의 페이지에 대한 기사를 수집하는 명령입니다. 자세한 사용법은 ``canrevan --help``를 참고하시기 바랍니다.
```console
$ canrevan --category 100 101 --start_date 20200501 --end_date 20200531 --max_page 5
```
성공적으로 뉴스 기사가 수집되었다면, 다음과 같은 출력을 확인할 수 있습니다.
```
[*] navigation pages: 310
[*] collect article urls: 100%|█████████████████████████████████████████████████████████████| 310/310 [00:05<00:00, 60.43it/s]
[*] total collected articles: 4998
[*] crawl news article contents: 100%|███████████████████████████████████████████████████| 4998/4998 [00:24<00:00, 200.41it/s]
[*] finish crawling 4781 news articles to [articles.txt]
```

## Format
`canrevan`은 수집된 뉴스 기사를 `json.encoder.encode_basestring`으로 인코딩합니다.

    "국방부는 18일부터 입대하는 모든 장정의 검체를 채취할 예정이며, 8주간 매주 6,300여명이 코로나19 검사를 받는다고 18일 밝혔다.\n군이 훈련소에서 자체적으로 검체를 채취하고, 질병관리본부와 계약을 맺은 민간 업체 등이 검체 이송과 검사를 담당한다. 대규모 인원의 빠른 검사를 위해 취합검사법(Pooling)이 활용된다.\n군 관계자는 “이태원 클럽 등으로 인해 코로나19 20대 감염 사례가 늘었다”며 “집단 생활하는 훈련병이 뒤늦게 코로나19 확진을 받으면 집단 감염이 발생할 수 있기 때문에 선제적으로 전원 검사를 시행한다”고 설명했다.\n군은 확진자가 나온 지역에서 입소하거나 확진자와 동선이 겹칠 경우에 예방적 격리와 검사를 시행했었다.\n현재까지 이태원 일대를 방문했다고 부대에 알린 훈련병 83명이 코로나19 검사를 받았고, 전원 음성 판정이 나왔다.\n훈련병이 입소 후 일주일 전 확진 판정을 받으면 귀가 조치되고, 일주일이 넘은 뒤 확진을 받으면 군 소속으로 치료를 받게 된다.\n앞서 지난달 13일 육군훈련소에 입소한 3명이 코로나19 확진 판정을 받아 귀가 조치됐다."

모든 수집된 뉴스 기사들은 위와 같은 포맷을 가지고 있습니다. `json.decoder.scanstring` 함수를 이용하여 개행 문자를 포함한 평문으로 디코딩할 수 있습니다.

## License
`canrevan`은 Apache-2.0 라이센스가 적용되어 있습니다.