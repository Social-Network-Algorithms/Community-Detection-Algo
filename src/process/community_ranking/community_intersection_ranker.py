from typing import List


class CommunityIntersectionRanker():
    def __init__(self, ranker_list):
        self.ranker_list = ranker_list
        self.ranking_function_name = None


    def rank(self, user_list: List[str], respection: List[str], mode: bool, do_sort=True):
        raise NotImplementedError("This method should be implemented by subclasses")
