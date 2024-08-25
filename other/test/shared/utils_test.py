import src.shared.utils as utils
from datetime import datetime, timedelta

# get_project_root tests

def test_getProjectRoot_returnsExpectedInput():
    path = utils.get_project_root()
    path_string = str(path)

    assert path_string.endswith("core")

# get_unique_list tests

def test_getUniqueList_emptyList_returnsEmptyList():
    in_list = []
    out_list = utils.get_unique_list(in_list)

    assert out_list == []

def test_getUniqueList_uniqueList_returnsSameList():
    in_list = ['Hello', 'Goodbye']
    out_list = utils.get_unique_list(in_list)

    in_list.sort()
    out_list.sort()

    assert out_list == in_list

def test_getUniqueList_duplicates_removesDuplicates():
    in_list = ['Goodbye', 'Hello', 'Hello']
    out_list = utils.get_unique_list(in_list)

    expected_list = ['Goodbye', 'Hello']

    out_list.sort()
    expected_list.sort()

    assert out_list == expected_list

# get_date tests

def test_getDate_validInput_returnsCorrect():
    year = 2020
    month = 2
    day = 25

    expected_date = datetime(year, month, day)

    date_str = str(year) + "-" + str(month) + "-" + str(day)
    actual_date = utils.get_date(date_str)

    assert expected_date == actual_date

# daterange tests

def test_daterange_zeroDays_returnsEmpty():
    today = datetime.now()

    expected_daterange = []

    actual_daterange = list(utils.daterange(today, today))

    assert expected_daterange == actual_daterange

def test_daterange_oneDay_returnsCorrect():
    today = datetime.now()
    tomorrow = today + timedelta(days = 1)

    expected_daterange = [today]

    actual_daterange = list(utils.daterange(today, tomorrow))

    assert expected_daterange == actual_daterange

def test_daterange_twoDays_returnsCorrect():
    today = datetime.now()
    tomorrow = today + timedelta(days = 1)
    last_day = today + timedelta(days = 2)

    expected_daterange = [today, tomorrow]

    actual_daterange = list(utils.daterange(today, last_day))

    assert expected_daterange == actual_daterange

# word_overlap tests

def test_wordOverlap_noOverlap_returnsZero():
    counter1 = {"Hello": 1}
    counter2 = {"Goodbye": 1}

    assert utils.word_overlap(counter1, counter2) == 0

def test_wordOverlap_overlap_returnsCorrect():
    counter1 = {"Hello": 1, "Goodbye": 1, "Yes": 15, "No": 20}
    counter2 = {"Hello": 1, "Goodbye": 3, "Maybe": 10}

    assert utils.word_overlap(counter1, counter2) == 2
