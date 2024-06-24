from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List


class CommunityFollowerRanker(CommunityRanker):
    def __init__(self, cluster_getter, user_getter, ranking_setter):
        self.cluster_getter = cluster_getter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "followers"

    def score_users(self, user_ids: List[str], respection: List[str]):
        users = self.user_getter.get_users_by_id_list(user_ids)

        scores = {}
        for user in users:
            scores[str(user.id)] = user.followers_count

        return scores
