from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List


class CommunityLocalFollowersRanker(CommunityRanker):
    def __init__(self, cluster_getter, user_getter, friends_getter, ranking_setter):
        self.cluster_getter = cluster_getter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "local_followers"
        self.friends_getter = friends_getter

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {}

        user_friends = {}
        for user in user_ids:
            user_friends[user] = [str(friend) for friend in self.friends_getter.get_user_friends_ids(user)] # list of int objects
        for user in user_ids:
            local_followers = 0
            for friend in user_ids:
                if user in user_friends[friend]:
                    local_followers += 1
            scores[user] = local_followers

        return scores
