import os
import json
from canrevan.parsing import extract_article_urls, parse_article_content


def _get_resource_content(name: str) -> str:
    res_path = os.path.join(os.path.dirname(__file__), 'resources', name)
    with open(res_path, 'r') as fp:
        return fp.read()


def test_extracting_article_urls():
    article_urls = extract_article_urls(_get_resource_content('nav_html'))
    article_urls = [url[55:] for url in article_urls]
    assert article_urls == ['sid1=100&sid2=265&oid=029&aid=0002625369',
                            'sid1=100&sid2=265&oid=079&aid=0003409069',
                            'sid1=100&sid2=265&oid=421&aid=0004881296',
                            'sid1=100&sid2=265&oid=421&aid=0004881295',
                            'sid1=100&sid2=265&oid=421&aid=0004881294',
                            'sid1=100&sid2=265&oid=001&aid=0011892040',
                            'sid1=100&sid2=265&oid=001&aid=0011892037',
                            'sid1=100&sid2=265&oid=001&aid=0011892036',
                            'sid1=100&sid2=265&oid=001&aid=0011892035',
                            'sid1=100&sid2=265&oid=001&aid=0011892034',
                            'sid1=100&sid2=265&oid=001&aid=0011892013',
                            'sid1=100&sid2=265&oid=014&aid=0004497351',
                            'sid1=100&sid2=265&oid=421&aid=0004881269',
                            'sid1=100&sid2=265&oid=468&aid=0000698806',
                            'sid1=100&sid2=265&oid=001&aid=0011891993',
                            'sid1=100&sid2=265&oid=001&aid=0011891992',
                            'sid1=100&sid2=265&oid=001&aid=0011891989',
                            'sid1=100&sid2=265&oid=001&aid=0011891986',
                            'sid1=100&sid2=265&oid=001&aid=0011891985',
                            'sid1=100&sid2=265&oid=001&aid=0011891984']


def test_parsing_article_contents():
    content = parse_article_content(_get_resource_content('article_html'))
    assert (json.decoder.scanstring(content, 1)[0]
            == '이재명 경기도지사가 19일 \"지자체에 지역화폐가 확산하면 단점이 '
               '심화할 수 있다\"고 지적한 국민의힘 윤희숙 의원을 향해 \"언론 뒤에 '
               '숨지 말고 공개 토론하자\"고 제안했다.\n'
               '이 지사는 이날 페이스북에서 \"경제 전문가인 윤희숙 위원장님, '
               '지역화폐는 소비의 지역 간 이전 차단보다 업종 내 규모별 재분배에 더 '
               '중점이 있다는 거 모르시진 않으시지요?\"라며 이같이 밝혔다.\n'
               '그는 \"유통 대기업의 골목상권 잠식으로 피해 보는 영세자영업자와 '
               '골목상권을 보호하는 지역화폐는 문재인 정부의 포용정책 중 하나\"'
               '라며 \"윤 의원은 비중이 적은 소비의 지역 이전 부분만 강조하고 '
               '핵심요소인 규모별 이전 효과는 의도적으로 외면하는 것 같다\"고 '
               '했다.\n'
               '이어 \"왜곡조작으로 기득권 옹호하는 일부 보수언론 뒤에 숨어 '
               '불합리한 일방적 주장만 하지 말고, 수차례 제안한 국민 앞 '
               '공개토론에서 당당하게 논쟁해 보실 용의는 없냐\"고 덧붙였다.\n'
               '윤 의원은 이날 페이스북에 \'지역화폐가 역효과를 낸다\'는 '
               '한국조세재정연구원(조세연)의 보고서에 대해 \"분석과 서술방식 모두 '
               '잘 쓰인 보고서\"라고 평가하며 \"지자체에 (지역화폐가) 확산하면 '
               '의도했던 장점은 줄고 단점만 심화할 수 있다\"고 지적했다. 또 이 '
               '지사의 조세연 비판을 두고 \"권력을 가진 이들이 전문가집단을 힘으로 '
               '찍어누르려 하는 것은 한 나라의 지적 인프라를 위협하는 일인 동시에 '
               '본인들 식견의 얕음을 내보이는 일\"이라고 날을 세웠다.')
