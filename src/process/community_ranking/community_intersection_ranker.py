from typing import List
from tqdm import tqdm
from src.shared.logger_factory import LoggerFactory
import statistics

log = LoggerFactory.logger(__name__)

class CommunityIntersectionRanker:
    def __init__(self, ranker_list):
        self.ranker_list = ranker_list
        self.ranking_function_name = "intersection"

    def rank(self, user_list: List[str], respection: List[str], mode: bool):

        log.info("User Length: " + str(len(user_list)))
        ranks = []
        for ranker in self.ranker_list:

            scores = {}
            for user in tqdm(user_list):
                scores[user] = ranker.score_user(user, respection)
                # if str(user) not in respection:
                #     scores[user] = ranker.score_user(user, respection + [str(user)])
                # else:
                #     scores[user] = ranker.score_user(user, respection)
            # scores = ranker.score_users(user_list)
            # print(scores)
            rank = [key for key, value in sorted(scores.items(), key=lambda x: (x[1], x[0]), reverse=True)]
            log.info("Rank length: " + str(len(rank)))
            # for i in range(0, len(rank)):
            #     if rank[i] == '1356595452':
            #         log.info(ranker.ranking_function_name + " rank for LawrenceTrentIM: " + str(i))
            #     elif rank[i] == '313299656':
            #         log.info(ranker.ranking_function_name + " rank for davidllada: " + str(i))

            ranks.append(rank)

        ranking = {}
        # i means top i users
        # print(ranks)
        if mode is True:
            for user in ranks[0]:
                rank_influence_1 = ranks[0].index(user)
                rank_influence_2 = ranks[1].index(user)
                rank_production = ranks[2].index(user)
                rank_consumption = ranks[3].index(user)
                inter_rank_1 = max(rank_influence_1, rank_influence_2)
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
                    if user not in ranking:
                        ranking[user] = i

        intersection_ranking = \
            [key for key, value in sorted(ranking.items(), key=lambda x: (x[1], x[0]), reverse=False)]
        log.info("Intersection Rank Length: " + str(len(intersection_ranking)))

        return intersection_ranking
        '''if user_list == []:
            return []

        scores_list = []
        for ranker in self.ranker_list:
            scores = []
            for user in user_list:
                scores.append(ranker.score_user(user, respection))
            scores_list.append(scores)
        average = [statistics.mean(scores) for scores in scores_list]
        std = [statistics.stdev(scores) for scores in scores_list]

        normalized_scores_list = []
        for i in range(0, len(scores_list)):
            normalized_scores = [(score - average[i]) / std[i] for score in scores_list[i]]
            normalized_scores_list.append(normalized_scores)

        weights = [1, 1, 1, 1]
        weighted_scores_dict = {}
        for i in range(0, len(user_list)):
            weighted_scores_dict[user_list[i]] = \
                sum([weights[j] * normalized_scores_list[j][i] for j in range(0, len(self.ranker_list))])

        intersection_ranking = \
            [key for key, value in sorted(weighted_scores_dict.items(), key=lambda x: (x[1], x[0]), reverse=True)]
        log.info("Intersection Rank Length: " + str(len(intersection_ranking)))

        return intersection_ranking '''
