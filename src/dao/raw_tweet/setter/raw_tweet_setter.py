from typing import List, Dict
from src.model.tweet import Tweet

class RawTweetSetter:
    """
    An abstract class representing an object that stores tweets in a
    datastore
    """
    def store_tweet(self, tweet: Tweet):
        raise NotImplementedError("Subclasses should implement this")

    def store_many_tweets(self, tweets: List[Tweet]):
        raise NotImplementedError("Subclasses should implement this")

    def get_num_user_tweets(self, user_id) -> int:
        raise NotImplementedError("Subclasses should implement this")

    def store_tweets(self, tweets: List[Tweet]) -> None:
        for tweet in tweets:
            self.store_tweet(tweet)
