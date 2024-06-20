from src.process.ranking.ranker import Ranker
from typing import List


class LocalFollowersRanker(Ranker):
    def __init__(self, twitter_getter, cluster_getter, user_getter, friends_getter, ranking_setter):
        self.twitter_getter = twitter_getter
        self.cluster_getter = cluster_getter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "local_followers"
        self.friends_getter = friends_getter

    def score_users(self, user_ids: List[str]):
        scores = {}

        user_friends = {}
        for user in user_ids:
            friends = self.friends_getter.get_user_friends_ids(user)
            if friends is None:
                _, friends = self.twitter_getter.get_friends_ids_by_user_id(user)
            user_friends[user] = friends  # list of int objects
        for user in user_ids:
            local_followers = 0
            for friend in user_ids:
                if user in user_friends[friend]:
                    local_followers += 1
            scores[user] = local_followers

        return scores
