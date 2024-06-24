from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List
from tqdm import tqdm


class LinearCommunityRanker(CommunityRanker):
    def __init__(self, user_tweets_getter: UserTweetsGetter):
        self.user_tweets_getter = user_tweets_getter
        self.ranking_function_name = "retweets"

    def score_users(self, users: List, current_community: List, gamma=3):
        """
        @param users: list of users' ids
        @param current_community: list of current community users' ids
        @param gamma: the rate coefficient of production utility / consumption utility
        """
        # calculate retweet score
        production_scores = {}
        consumption_scores = {}
        for id in users:
            production_scores[id] = 0
            consumption_scores[id] = 0

        for id in tqdm(users):
            retweets = self.user_tweets_getter.get_user_retweets(id)
            if len(retweets) < 1:
                production_scores[id] = 0
                continue
            for retweet in retweets:
                if (str(retweet.user_id) in current_community) or (int(retweet.user_id) in current_community):
                    if int(retweet.user_id) != int(id):
                        production_scores[id] += 1

        for id in tqdm(users):
            retweets = self.user_tweets_getter.get_retweets_by_user_id_time_restricted(id)
            for retweet in retweets:
                if str(retweet.retweet_user_id) in current_community or int(
                        retweet.retweet_user_id) in current_community:
                    if str(retweet.retweet_user_id) != str(id):  # retweeting your own tweet does not count
                        consumption_scores[id] += 1

        scores = {}
        for id in users:
            scores[id] = consumption_scores[id] + production_scores[id] * gamma
        return scores
