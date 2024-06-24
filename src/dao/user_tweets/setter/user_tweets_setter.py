from typing import List

from src.model.tweet import Tweet


class UserTweetsSetter:
    """
    An abstract class representing an object that stores all of a users
    tweets in a datastore
    """

    def store_tweets(self, user_id: str, tweets: List[Tweet]):
        raise NotImplementedError("Subclasses should implement this")

    def add_user_tweets(self, user_id: str, tweets: List[Tweet]):
        raise NotImplementedError("Subclasses should implement this")