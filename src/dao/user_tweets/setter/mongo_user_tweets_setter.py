from typing import List

from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.model.tweet import Tweet


class MongoUserTweetsSetter(UserTweetsSetter):
    def __init__(self):
        self.user_tweets_collection = None

    def set_user_tweets_collection(self, user_tweets_collection: str) -> None:
        self.user_tweets_collection = user_tweets_collection

    def store_tweets(self, user_id: str, tweets: List[Tweet]):
        doc = {"user_id": str(user_id), "tweets": list(map(lambda tweet: tweet.__dict__, tweets))}

        if self.contains_user(user_id):
            self.user_tweets_collection.find_one_and_replace({"user_id": str(user_id)}, doc)
        else:
            self.user_tweets_collection.insert_one(doc)

    def add_user_tweets(self, user_id: str, tweets: List[Tweet]):
        doc = {"user_id": str(user_id), "tweets": list(map(lambda tweet: tweet.__dict__, tweets))}
        existing_doc = self.user_tweets_collection.find_one({"user_id": str(user_id)})

        if existing_doc is not None:
            doc["tweets"] += existing_doc["tweets"]
            self.user_tweets_collection.find_one_and_replace({"user_id": str(user_id)}, doc)
        else:
            self.user_tweets_collection.insert_one(doc)

    def contains_user(self, user_id: str) -> bool:
        return self.user_tweets_collection.find_one({"user_id": str(user_id)}) is not None
