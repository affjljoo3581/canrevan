from canrevan.utils import drange, korean_character_ratio, is_normal_character


def test_drange():
    assert (drange('20200501', '20200531')
            == ['202005{:02d}'.format(d) for d in range(1, 31 + 1)])
    assert (drange('20200401', '20200531')
            == (['202004{:02d}'.format(d) for d in range(1, 30 + 1)]
                + ['202005{:02d}'.format(d) for d in range(1, 31 + 1)]))


def test_korean_character_ratio():
    ratio = korean_character_ratio(
        '위키백과(Wiki百科, IPA: [ɥikçibɛ̝k̚k͈wa̠], [ykçibɛ̝k̚k͈wa̠] ( 듣기)) 또는 '
        '위키피디아(영어: Wikipedia, IPA: [ˌwɪkɪˈpiːdɪə] ( 듣기))는 누구나 '
        '자유롭게 쓸 수 있는 다언어판 인터넷 백과사전이다.[1] 2001년 1월 15일 지미 '
        '웨일스와 래리 생어가 시작하였으며[2], 대표적인 집단 지성의 사례로 평가받고 '
        '있다.[3]')
    assert 0.44 < ratio and ratio < 0.45

    ratio = korean_character_ratio(
        'Wikipedia (/ˌwɪkɪˈpiːdiə/ (About this soundlisten) wik-ih-PEE-dee-ə '
        'or /ˌwɪkiˈpiːdiə/ (About this soundlisten) wik-ee-PEE-dee-ə; '
        'abbreviated as WP) is a multilingual online encyclopedia created and '
        'maintained as an open collaboration project[4] by a community of '
        'volunteer editors using a wiki-based editing system.[5] It is the '
        'largest and most popular general reference work on the World Wide '
        'Web.[6][7][8] It is also one of the 15 most popular websites as '
        'ranked by Alexa, as of August 2020.[9] It features exclusively free '
        'content and has no advertising. It is hosted[10] by the Wikimedia '
        'Foundation, an American non-profit organization funded primarily '
        'through donations.[11][12][13][14]')
    assert ratio == 0


def test_normal_characters():
    assert is_normal_character('하')
    assert is_normal_character('1')
    assert is_normal_character('a')
    assert is_normal_character('Z')

    assert not is_normal_character('ㄴ')
    assert not is_normal_character('(')
    assert not is_normal_character('.')
    assert not is_normal_character('\'')
