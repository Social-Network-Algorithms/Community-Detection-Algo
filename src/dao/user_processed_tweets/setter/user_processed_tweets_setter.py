class UserProcessedTweetsSetter:
    """
    An abstract class representing an object that stores all of a users
    processed tweets in a datastore
    """

    def store_processed_tweets(self, user_id: str, tweets):
        raise NotImplementedError("Subclasses should implement this")

    def add_processed_tweets(self, user_id: str, tweets):
        raise NotImplementedError("Subclasses should implement this")
