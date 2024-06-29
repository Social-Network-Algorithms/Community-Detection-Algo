from typing import List
from tqdm import tqdm

from src.process.community_ranking.community_intersection_ranker import CommunityIntersectionRanker
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)


class CommunityIntersectionRankerAll(CommunityIntersectionRanker):
    """ Intersection ranker for the 4 ranking functions: Influence 1, Influence 2, Production Utility, Consumption
    Utility"""
    def __init__(self, ranker_list):
        self.ranker_list = ranker_list
        self.ranking_function_name = "intersection"

    def rank(self, user_list: List[str], respection: List[str], mode: bool, do_sort=True):

        log.info("User Length: " + str(len(user_list)))
        ranks = []
        for ranker in self.ranker_list:

            scores = {}
            for user in tqdm(user_list):
                scores[user] = ranker.score_user(user, respection)
            rank = [key for key, value in sorted(scores.items(), key=lambda x: (x[1], x[0]), reverse=True)]
            log.info("Rank length: " + str(len(rank)))

            ranks.append(rank)

        ranking = {}
        for user in user_list:
            ranking[user] = None

        # i means top i users
        if mode is True:
            for user in user_list:
                rank_influence_1 = ranks[0].index(user)
                rank_influence_2 = ranks[1].index(user)
                rank_production = ranks[2].index(user)
                rank_consumption = ranks[3].index(user)
                inter_rank_1 = min(rank_influence_1, rank_influence_2)
                intersection_rank = max(inter_rank_1, rank_production, rank_consumption)
                ranking[user] = intersection_rank
        else:
            for i in range(len(ranks[0])):
                # find users that are in the intersection of top i of each rank
                intersection_users = set(ranks[0][:i + 1])
                for j in range(1, len(ranks)):
                    intersection_users = intersection_users.intersection(
                        set(ranks[j][:i + 1]))
                for user in intersection_users:
                    if ranking[user] is None:
                        ranking[user] = i
            for user in ranking:
                if ranking[user] is None:
                    # remove an unranked user
                    ranking.pop(user)

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
