from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.process.ranking.ranker import Ranker
from typing import Dict, List
from tqdm import tqdm


class InfluenceOneRanker(Ranker):
    def __init__(self, twitter_getter, user_tweets_getter: UserTweetsGetter, user_tweets_setter: UserTweetsSetter,
                 friends_getter, friends_setter, ranking_setter):
        self.twitter_getter = twitter_getter
        self.user_tweets_getter = user_tweets_getter
        self.user_tweets_setter = user_tweets_setter
        self.friends_getter = friends_getter
        self.friends_setter = friends_setter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "influence one"

    def create_friends_dict(self, user_ids):
        friends = {}
        for user_id in user_ids:
            friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)
            if friends_of_user_id is None:
                _, friends_result = self.twitter_getter.get_friends_ids_by_user_id(user_id, None)
                self.friends_setter.store_friends(user_id, friends_result)
                friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)

            friends[user_id] = friends_of_user_id
        return friends

    def score_users(self, user_ids: List[str]):
        # Score users with their average number of retweets from direct followers
        friends = self.create_friends_dict(user_ids)
        scores = {user_id: [0, 0] for user_id in user_ids}  # Initialize all scores to 0

        tweets = []
        for id in user_ids:
            user_tweets = self.user_tweets_getter.get_user_tweets(id)
            if user_tweets is None:
                self.user_tweets_setter.store_tweets(id, self.twitter_getter.get_tweets_by_user_id(id, 600))
                user_tweets = self.user_tweets_getter.get_user_tweets(id)

            tweets += user_tweets
        valid_tweets = [tweet for tweet in tweets if tweet.retweet_user_id != tweet.user_id]  # omit self-retweets

        # Define helper functions
        # NOTE: The get_retweets functions are dependent on valid_tweets and therefore user_ids
        # i.e. retweets of tweet id by users in user_ids
        tweets_by_retweet_group = self._group_by_retweet_id(valid_tweets)

        def get_retweets_of_tweet_id(tweet_id):
            return tweets_by_retweet_group.get(str(tweet_id), [])

        def get_later_retweets_of_tweet_id(tweet_id, created_at):
            return [tweet for tweet in get_retweets_of_tweet_id(tweet_id) if tweet.created_at > created_at]

        def is_direct_follower(a, b):
            # b follows a
            return a in friends.get(b, [])

        for id in tqdm(user_ids):
            user_tweets = [tweet for tweet in valid_tweets if str(tweet.user_id) == id]

            # Score original tweets
            user_original_tweets = [tweet for tweet in user_tweets if tweet.retweet_id is None]
            for original_tweet in user_original_tweets:
                retweets = get_retweets_of_tweet_id(original_tweet.id)
                retweets_from_direct_followers = [rtw for rtw in retweets if is_direct_follower(id, str(rtw.user_id))]
                scores[id][0] += len(retweets_from_direct_followers)

            # Score retweets
            user_retweets = [tweet for tweet in user_tweets if tweet.retweet_id is not None]
            for user_retweet in user_retweets:
                retweets = get_later_retweets_of_tweet_id(user_retweet.retweet_id, user_retweet.created_at)
                # The person who retweeted is a direct follower of id.
                retweets_from_direct_followers = [rtw for rtw in retweets if is_direct_follower(id, str(rtw.user_id))]
                scores[id][0] += len(retweets_from_direct_followers)

            if len(user_tweets) > 0:
                scores[id][0] /= len(user_tweets)
            scores[id][1] = len(user_tweets)
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
