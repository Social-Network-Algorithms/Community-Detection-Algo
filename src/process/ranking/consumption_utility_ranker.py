from src.dao.bluesky.bluesky_dao import BlueSkyGetter
from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.process.ranking.ranker import Ranker
from typing import List
from tqdm import tqdm


class ConsumptionUtilityRanker(Ranker):
    def __init__(self, bluesky_getter: BlueSkyGetter, cluster_getter, user_tweets_getter: UserTweetsGetter,
                 user_tweets_setter: UserTweetsSetter, user_getter, ranking_setter):
        self.bluesky_getter = bluesky_getter
        self.cluster_getter = cluster_getter
        self.user_tweets_getter = user_tweets_getter
        self.user_tweets_setter = user_tweets_setter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "consumption utility"

    def score_users(self, user_ids: List[str]):
        scores = {user_id: [0, 0] for user_id in user_ids} # Initialize all scores to 0
        for id in tqdm(user_ids):
            user = self.user_getter.get_user_by_id(id)
            scores[id][1] = user.friends_count
            user_tweets = self.user_tweets_getter.get_user_tweets(id)
            if user_tweets is None:
                self.user_tweets_setter.store_tweets(id, self.bluesky_getter.get_tweets_by_user_id(id, 600))
                user_tweets = self.user_tweets_getter.get_user_tweets(id)

            for tweet in user_tweets:
                if tweet.retweet_id is not None and \
                        str(tweet.retweet_user_id) in user_ids and \
                        str(tweet.retweet_user_id) != str(id):
                    scores[str(id)][0] += 1

        # for id in tqdm(user_ids):
        #     user = self.user_getter.get_user_by_id(id)
        #     scores[id][1] = user.friends_count
                # retweets = self.raw_tweet_getter.get_retweets_by_user_id_time_restricted(id)
                # # coefficient = self.raw_tweet_getter.get_tweet_scale_coefficient(id)
                # for retweet in retweets:
                #     if str(retweet.retweet_user_id) in user_ids and str(retweet.retweet_user_id) != str(id): # retweeting your own tweet does not count
                #         scores[id][0] += 1
                # scores[str(id)] *= coefficient
        return scores
