from typing import List

from src.process.community_ranking.community_intersection_ranker import CommunityIntersectionRanker
from src.shared.logger_factory import LoggerFactory
import statistics

log = LoggerFactory.logger(__name__)


class CommunitySSIntersectionRanker(CommunityIntersectionRanker):
    """ Intersection ranker for the 2 ranking functions: Influence 1 and social support"""
    def __init__(self, ranker_list):
        self.influence1_ranker = ranker_list[0]
        self.social_support_ranker = ranker_list[1]
        self.ranking_function_name = "intersection"

    def rank(self, user_list: List[str], respection: List[str], mode, do_sort=True):
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

        for user in user_list:
            rank_influence1 = ranks[0].index(user)
            rank_social_support = ranks[1].index(user)
            intersection_rank = max(rank_influence1, rank_social_support)
            ranking[user] = intersection_rank

        if do_sort:
            sorted_ranking = sorted(ranking.items(), key=lambda x: (x[1], x[0]), reverse=False)
            intersection_ranking_users = \
                [key for key, value in sorted_ranking]
            intersection_ranking_scores = \
                [value for key, value in sorted_ranking]

            log.info("Intersection Rank Length: " + str(len(intersection_ranking_users)))

            return intersection_ranking_users, intersection_ranking_scores

        else:
            return list(ranking.keys()), list(ranking.values())

