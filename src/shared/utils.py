from datetime import datetime, timedelta
from typing import List, Dict, Iterator
from pathlib import Path
import math

"""
This file contains utility methods
"""


def get_project_root() -> Path:
    """
    Returns a path object corresponding to the project root

    @retun path of the project root
    """
    return Path(__file__).parent.parent.parent


def get_unique_list(lst: List) -> List:
    """
    Returns the input list with duplicates removed

    @param lst the input List
    @return the given list with duplicates removed
    """
    return list(set(lst))


def get_date(date_str: str) -> datetime:
    """
    Given a date format of the form "year-month-date", parses the string to a
    datetime object

    @param date_str
    """
    year, month, day = map(int, date_str.split('-'))
    return datetime(year, month, day)


def daterange(start_date: datetime, end_date: datetime) -> Iterator[datetime]:
    """
    Given a start date and end date, return a sequence containing every day in
    the range from the start to the end (not including the end date)

    @param start_date the start date of the date range
    @param end_date the end date of the date range

    @return a generator containing a datetime object for each day starting on
    start_date, and ending on end_date (not including end_date)
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days=n)


def cosine_sim(counter1: Dict[str, int], counter2: Dict[str, int]) -> float:
    """
    An implementation of cosine similarity based on word counters rather than vectors

    @param counter1 The first word vector to compare
    @param counter2 The second word vector to compare
    """

    norm_c1 = sum([x**2 for x in counter1.values()])**0.5
    norm_c2 = sum([x**2 for x in counter2.values()])**0.5
    dot_product = 0
    for key in set.intersection(set(counter1.keys()), set(counter2.keys())):
        dot_product += counter1[key]*counter2[key]

    return dot_product/(norm_c1*norm_c2) if norm_c1 != 0 and norm_c2 != 0 else -1


def word_overlap(counter1: Dict[str, int], counter2: Dict[str, int]) -> int:
    """
    Find the number of overlapping words between two counters

    @param counter1 The first word vector to compare
    @param counter2 The second word vector to compare

    @return the number of overlapping words in the two counters
    """

    set1 = set(counter1.keys())
    set2 = set(counter2.keys())

    return len(set.intersection(set1, set2))


def parse_bool(input: str) -> bool:
    """
    Parses a string to a boolean

    @param input the string to parse
    @return the parsed boolean
    """
    bool(distutils.util.strtobool(input))


def passes_interval(i, total, interval):
    current_percent = i/total * 100
    previous_percent = (i - 1)/total * 100

    return int(current_percent/interval) > int(previous_percent/interval)


def print_progress(i, total):
    percent_done = i/total * 100
    if passes_interval(i, total, 2):
        print("Done " + str(math.floor(percent_done)) + "% of process")

def jaccard_similarity(user_list1, user_list2):
    intersection = len(set(user_list1).intersection(set(user_list2)))
    union = (len(user_list1) + len(user_list2)) - intersection
    if union == 0:
        return 0
    return float(intersection) / union