from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.process.ranking.ranker import Ranker
from typing import Dict, List
from tqdm import tqdm

class SocialSupportRanker(Ranker):
    def __init__(self, bluesky_getter, user_tweets_getter: UserTweetsGetter, user_tweets_setter: UserTweetsSetter,
                 user_getter, friends_getter, friends_setter, ranking_setter, alpha=1.0):
        self.bluesky_getter = bluesky_getter
        self.friends_getter = friends_getter
        self.friends_setter = friends_setter
        self.user_tweets_getter = user_tweets_getter
        self.user_tweets_setter = user_tweets_setter
        self.user_getter = user_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "retweets"
        self.alpha = alpha

    def create_friends_dict(self, user_ids):
        friends = {}
        for user_id in user_ids:
            friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)
            if friends_of_user_id is None:
                _, friends_result = self.bluesky_getter.get_friends_ids_by_user_id(user_id, None)
                self.friends_setter.store_friends(user_id, friends_result)
                friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)

            friends[user_id] = friends_of_user_id
        return friends

    def score_users(self, user_ids: List[str]):
        scores = {user_id: [0, 0] for user_id in user_ids} # Initialize all scores to 0
        friends = self.create_friends_dict(user_ids)
        # tweets = self.raw_tweet_getter.get_tweets_by_user_ids(user_ids)
        tweets = []
        for id in user_ids:
            user_tweets = self.user_tweets_getter.get_user_tweets(id)
            if user_tweets is None:
                self.user_tweets_setter.store_tweets(id, self.bluesky_getter.get_tweets_by_user_id(id, 600))
                user_tweets = self.user_tweets_getter.get_user_tweets(id)

            tweets += user_tweets
        # Omit self-retweets
        tweets = [tweet for tweet in tweets if tweet.user_id != tweet.retweet_user_id]
        tweets_by_retweet_group = self._group_by_retweet_id(tweets)
        def get_retweets_of_tweet_id(tweet_id):
            return tweets_by_retweet_group.get(tweet_id, [])
        def get_later_retweets_of_tweet_id(tweet_id, created_at):
            return [tweet for tweet in get_retweets_of_tweet_id(tweet_id) if tweet.created_at > created_at]
        def is_direct_follower(a, b):
            # b follows a
            return a in friends.get(b, [])

        for id in tqdm(user_ids):
            user = self.user_getter.get_user_by_id(id)
            scores[id][1] = user.followers_count
            user_tweets = [tweet for tweet in tweets if str(tweet.user_id) == id]
            original_tweet_ids = [tweet.id for tweet in user_tweets if tweet.retweet_id is None]

            for original_tweet_id in original_tweet_ids:
                retweets = get_retweets_of_tweet_id(original_tweet_id)
                scores[id][0] += len(retweets)

            user_retweets = [tweet for tweet in user_tweets if tweet.retweet_id is not None]
            for user_retweet in user_retweets:
                retweets = get_later_retweets_of_tweet_id(user_retweet.retweet_id, user_retweet.created_at)
                # The person who retweeted is a direct follower of id.
                retweets_from_direct_followers = [rtw for rtw in retweets if is_direct_follower(id, str(rtw.user_id))]
                scores[id][0] += len(retweets_from_direct_followers) * self.alpha

        return scores

    def _group_by_retweet_id(self, tweets) -> Dict:
        # Puts all tweets with the same retweet_id in the same list
        # Returns: A dictionary where the key is the retweet_id and
        # the value is the list of tweets with that retweet_id
        retweet_id_map = {}
        for tweet in tweets:
            key = str(tweet.retweet_id)
            if key in retweet_id_map:
                retweet_id_map[key].append(tweet)
            else:
                retweet_id_map[key] = [tweet]

        return retweet_id_map
