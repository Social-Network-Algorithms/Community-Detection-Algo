from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.process.ranking.ranker import Ranker
from typing import Dict, List
from tqdm import tqdm


class ProductionUtilityRanker(Ranker):
    def __init__(self, twitter_getter, cluster_getter, user_tweets_getter: UserTweetsGetter,
                 user_tweets_setter: UserTweetsSetter, user_getter, ranking_setter):
        self.twitter_getter = twitter_getter
        self.cluster_getter = cluster_getter
        self.user_tweets_getter = user_tweets_getter
        self.user_tweets_setter = user_tweets_setter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "retweets"

    def score_users(self, user_ids: List[str]):
        scores = {user_id: [0, 0] for user_id in user_ids}  # Initialize all scores to 0
        tweets = []
        for id in user_ids:
            user = self.user_getter.get_user_by_id(id)
            scores[id][1] = user.followers_count

            user_tweets = self.user_tweets_getter.get_user_tweets(id)
            if user_tweets is None:
                self.user_tweets_setter.store_tweets(id, self.twitter_getter.get_tweets_by_user_id(id, 600))
                user_tweets = self.user_tweets_getter.get_user_tweets(id)
            tweets += user_tweets

        tweets_by_retweet_group = self._group_by_retweet_id(tweets)

        def get_retweets_of_tweet_id(tweet_id):
            return tweets_by_retweet_group.get(str(tweet_id), [])

        for id in tqdm(user_ids):
            original_tweet_ids = [tweet.id for tweet in tweets if str(tweet.user_id) == id and tweet.retweet_id is None]
            for original_tweet_id in original_tweet_ids:
                retweets = get_retweets_of_tweet_id(original_tweet_id)
                valid_retweets = [retweet for retweet in retweets if
                                  retweet.retweet_user_id != retweet.user_id]  # omit self-retweets
                scores[id][0] += len(valid_retweets)

        return scores

    def _group_by_retweet_id(self, tweets) -> Dict:
        # Puts all tweets with the same retweet_id in the same list
        # Returns: A dictionary where the key is the retweet_id and
        # the value is the list of tweets with that retweet_id
        dict = {}
        for tweet in tweets:
            key = str(tweet.retweet_id)
            if key in dict:
                dict[key].append(tweet)
            else:
                dict[key] = [tweet]

        return dict
