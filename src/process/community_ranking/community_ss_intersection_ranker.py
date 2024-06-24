from typing import List
from src.shared.logger_factory import LoggerFactory
import statistics

log = LoggerFactory.logger(__name__)


class CommunitySSIntersectionRanker:

    def __init__(self, ranker_list):
        self.influence1_ranker = ranker_list[0]
        self.social_support_ranker = ranker_list[1]
        self.ranking_function_name = "intersection"

    def rank(self, user_list: List[str], respection: List[str], mode: bool):
        log.info("User Length: " + str(len(user_list)))
        ranks = []

        influence1_scores = self.influence1_ranker.score_users(user_list, respection)
        social_support_scores = self.social_support_ranker.score_users(user_list, respection)

        influence1_rank = [key for key, value in
                           sorted(influence1_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)]
        social_support_rank = [key for key, value in
                               sorted(social_support_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)]

        ranks.append(influence1_rank)
        ranks.append(social_support_rank)

        ranking = {}

        for user in ranks[0]:
            rank_influence1 = ranks[0].index(user)
            rank_social_support = ranks[1].index(user)
            intersection_rank = max(rank_influence1, rank_social_support)
            ranking[user] = intersection_rank

        intersection_ranking = \
            [key for key, value in sorted(ranking.items(), key=lambda x: (x[1], x[0]), reverse=False)]
        log.info("Intersection Rank Length: " + str(len(intersection_ranking)))

        return intersection_ranking
