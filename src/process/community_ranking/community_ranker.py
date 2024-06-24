from src.model.ranking import Ranking
from typing import List


class CommunityRanker():
    def __init__(self, cluster_getter, user_getter, ranking_setter):
        self.cluster_getter = cluster_getter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = None

    def rank(self, seed_id, cluster):
        user_ids = cluster.users

        scores = self.score_users(user_ids, user_ids)

        ranked_ids = list(sorted(scores, key=scores.get, reverse=True))
        ranking = Ranking(seed_id, ranked_ids, self.ranking_function_name, {})

        self.ranking_setter.store_ranking(ranking)
        return ranking, scores

    def score_users(self, user_ids: List[str], respection: List[str]):
        raise NotImplementedError("This method should be implemented by subclasses")

    def score_user(self, user_id: str, user_ids: List[str]):
        raise NotImplementedError("This method should be implemented by subclasses")