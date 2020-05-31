# canrevan

[![PyPI version](https://badge.fury.io/py/canrevan.svg)](https://badge.fury.io/py/canrevan)
![build](https://github.com/affjljoo3581/canrevan/workflows/build/badge.svg)
[![GitHub license](https://img.shields.io/github/license/affjljoo3581/canrevan)](https://github.com/affjljoo3581/canrevan/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/affjljoo3581/canrevan/branch/master/graph/badge.svg)](https://codecov.io/gh/affjljoo3581/canrevan)
[![CodeFactor](https://www.codefactor.io/repository/github/affjljoo3581/canrevan/badge)](https://www.codefactor.io/repository/github/affjljoo3581/canrevan)

## Introduction
**canrevan**은 대량의 네이버 뉴스 기사를 수집하는 라이브러리입니다. 간단하게 한국어 뉴스
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
있습니다. 파싱하기 쉽습니다.
* 다양한 분야의 문서가 존재합니다. 뉴스 기사는 분야와 주제를 가리지 않습니다. 정치, 사회,
경제 등등의 주제를 다룹니다.

[네이버 뉴스](https://news.naver.com/)는 각 언론사의 뉴스를 종합하여 제공합니다. 하나의
플랫폼에서 다양한 언론사의 방대한 뉴스 기사를 수집할 수 있습니다. 실제로 많은 연구자들이
네이버 뉴스를 통해 기사를 수집합니다.

**canrevan**은 네이버 뉴스에서 기사를 수집하도록 도와줍니다. 명령창에서 한 줄로 수
기가바이트의 데이터를 손쉽게 수집할 수 있습니다. 자세한 내용은 [여기](#Example)를
참고하시기 바랍니다.

## Dependencies
* tqdm>=4.46.0
* kss==1.3.1
* bs4
* lxml>=4.5.1

## Installation
### With pip
canrevan은 pypi에 등록되어 있습니다. pip 명령어를 통해 쉽게 설치할 수 있습니다.
```console
$ pip install canrevan
```

### From source
pip을 이용하는 대신, 소스코드에서 직접 빌드하여 설치할 수 있습니다.
```console
$ git clone https://github.com/affjljoo3581/canrevan.git
$ cd canrevan
$ python setup.py install
```

## Example
수집하고자 하는 카테고리의 id를 [네이버 뉴스](https://news.naver.com/)에서 확인합니다. 이 예제에서는 정치(100)와 경제(101) 카테고리에 대한 뉴스를 수집하겠습니다. 다음은 2020년 5월 1일부터 31일까지 5개의 페이지에 대한 기사를 수집하는 명령입니다. 자세한 명령 사용법은 ``canrevan --help``를 입력하시기 바랍니다.
```console
$ canrevan --category 100 101 --start 20200501 --end 20200531 --max_page 5
```
성공적으로 뉴스 기사가 수집되었다면, 다음과 같은 출력을 확인할 수 있습니다.
```
[*] collect article urls: 100%|█████████████████| 62/62 [00:32<00:00,  1.93it/s]
[*] successfully collecting article urls. total articles: 6200
[*] crawl articles: 100%|███████████████████| 6200/6200 [04:11<00:00, 24.63it/s]
[*] finish crawling articles. merge chunks into [articles.txt].
```

## Expanda Extension
**canrevan**은 편리한 데이터셋 구성을 위해 **[Expanda](https://github.com/affjljoo3581/Expanda) extension**을 지원합니다. canrevan의 extension name은 ``canrevan.ext``이며, ``expanda show canrevan.ext``로 정보를 확인할 수 있습니다. 기본적인 설정파일 구조는 다음과 같습니다.
```ini
[canrevan.ext]
num-cores       = 6
min-length      = 50

# ...

[build]
input-files         =
    --canrevan.ext  src/articles.txt

# ...
```