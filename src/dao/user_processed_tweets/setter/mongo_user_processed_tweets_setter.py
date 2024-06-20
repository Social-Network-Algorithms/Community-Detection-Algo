from typing import List

from src.dao.user_processed_tweets.setter.user_processed_tweets_setter import UserProcessedTweetsSetter
from src.model.processed_tweet import ProcessedTweet


class MongoUserProcessedTweetsSetter(UserProcessedTweetsSetter):
    def __init__(self):
        self.user_processed_tweets_collection = None

    def set_user_tweets_collection(self, user_processed_tweets_collection: str) -> None:
        self.user_processed_tweets_collection = user_processed_tweets_collection

    def store_processed_tweets(self, user_id: str, tweets: List[ProcessedTweet]):
        doc = {"user_id": str(user_id), "tweets": list(map(lambda tweet: tweet.toDict(), tweets))}

        if self.contains_user(user_id):
            self.user_processed_tweets_collection.find_one_and_replace({"user_id": str(user_id)}, doc)
        else:
            self.user_processed_tweets_collection.insert_one(doc)

    def add_processed_tweets(self, user_id: str, tweets: List[ProcessedTweet]):
        doc = {"user_id": str(user_id), "tweets": list(map(lambda tweet: tweet.toDict(), tweets))}
        existing_doc = self.user_processed_tweets_collection.find_one({"user_id": str(user_id)})

        if existing_doc is not None:
            doc["tweets"] += existing_doc["tweets"]
            self.user_processed_tweets_collection.find_one_and_replace({"user_id": str(user_id)}, doc)
        else:
            self.user_processed_tweets_collection.insert_one(doc)

    def contains_user(self, user_id: str) -> bool:
        return self.user_processed_tweets_collection.find_one({"user_id": str(user_id)}) is not None
