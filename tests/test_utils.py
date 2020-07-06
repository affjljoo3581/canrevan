from canrevan.utils import (drange,
                            random_filename,
                            random_filenames,
                            split_list,
                            Context)
import asyncio


def test_context_run():
    async def test_fn(i):
        await asyncio.sleep(0.1)
        return i

    ctx = Context(max_tasks=10)
    result, errors = asyncio.run(ctx.run(test_fn(i) for i in range(100)))

    assert errors == 0
    assert set(result) == set(range(100))


def test_drange_creates_correct_date_range():
    # Test the range between 2020.5.1 and 2020.5.31.
    start, end = '20200501', '20200531'
    expected = ['202005{:02d}'.format(day) for day in range(1, 31 + 1)]
    assert drange(start, end) == expected


def test_generate_correct_filenames():
    # Check for single generation.
    assert len(random_filename('')) == 16
    assert random_filename('parent').startswith('parent')

    # Check for multiple generations.
    filenames = random_filenames('', n=4)
    assert len(filenames) == 4
    for name in filenames:
        assert len(name) == 16

    filenames = random_filenames('parent', n=4)
    for name in filenames:
        assert name.startswith('parent')


def test_list_is_split_well():
    # Check for factorizable list.
    seq = list(range(12))
    assert split_list(seq, 4) == [list(range(i * 3, (i + 1) * 3))
                                  for i in range(4)]

    # Check for non-factorizable list.
    seq = list(range(13))
    assert split_list(seq, 4) == ([list(range(i * 3, (i + 1) * 3))
                                   for i in range(3)]
                                  + [[9, 10, 11, 12]])
