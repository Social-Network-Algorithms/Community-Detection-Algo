from typing import List

from src.dao.user_processed_tweets.getter.user_processed_tweets_getter import UserProcessedTweetsGetter
from src.model.processed_tweet import ProcessedTweet


class MongoUserProcessedTweetsGetter(UserProcessedTweetsGetter):
    def __init__(self):
        self.user_processed_tweets_collection = None

    def get_all_processed_tweets(self) -> List[ProcessedTweet]:
        all_tweets = []
        docs = self.user_processed_tweets_collection.find()
        for doc in docs:
            all_tweets += list(map(lambda tweet: ProcessedTweet.fromDict(tweet), doc["tweets"]))
        return all_tweets

    def set_user_tweets_collection(self, user_processed_tweets_collection: str) -> None:
        self.user_processed_tweets_collection = user_processed_tweets_collection

    def get_user_processed_tweets(self, user_id: str) -> List[ProcessedTweet]:
        """Given a user id, return the processed tweets"""
        doc = self.user_processed_tweets_collection.find_one({"user_id":str(user_id)})
        if doc is not None:
            return list(map(lambda tweet: ProcessedTweet.fromDict(tweet), doc["tweets"]))
        else:
            return None

    def contains_user(self, user_id: str) -> bool:
        return self.user_processed_tweets_collection.find_one({"user_id": str(user_id)}) is not None
