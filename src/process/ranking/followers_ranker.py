from src.process.ranking.ranker import Ranker
from typing import List


class FollowerRanker(Ranker):
    def __init__(self, bluesky_getter, cluster_getter, user_getter, ranking_setter):
        self.bluesky_getter = bluesky_getter
        self.cluster_getter = cluster_getter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "followers"

    def score_users(self, user_ids: List[str]):
        scores = {}
        for user_id in user_ids:
            user = self.user_getter.get_user_by_id(user_id)
            scores[user_id] = user.followers_count

        return scores
