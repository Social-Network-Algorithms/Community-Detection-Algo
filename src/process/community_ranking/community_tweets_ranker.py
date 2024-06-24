from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List


class CommunityTweetsRanker(CommunityRanker):
    def __init__(self, cluster_getter, user_tweets_getter: UserTweetsGetter, ranking_setter):
        self.cluster_getter = cluster_getter
        self.user_tweets_getter = user_tweets_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "tweets"

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {}
        for id in user_ids:
            tweets = self.user_tweets_getter.get_user_tweets(id)

            count = 0
            for tweet in tweets:
                if str(tweet.user_id) in user_ids:
                    count += 1

            scores[str(id)] = count

        return scores
