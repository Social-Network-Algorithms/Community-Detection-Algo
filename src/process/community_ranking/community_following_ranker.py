from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List


class CommunityFollowingRanker(CommunityRanker):
    def __init__(self, user_getter):
        self.user_getter = user_getter
        self.ranking_function_name = "following"

    def score_users(self, user_ids: List[str], respection: List[str]):
        users = self.user_getter.get_users_by_id_list(user_ids)

        scores = {}
        for user in users:
            if user is not None:
                scores[user.id] = user.friends_count

        return scores
