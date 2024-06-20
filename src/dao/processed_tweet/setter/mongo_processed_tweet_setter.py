from typing import List, Dict, Set
from pymongo import InsertOne
from src.dao.processed_tweet.setter.processed_tweet_setter import ProcessedTweetSetter
from src.dao.mongo.mongo_dao import MongoDAO
from src.model.processed_tweet import ProcessedTweet
from src.model.tweet import Tweet


class MongoProcessedTweetSetter(ProcessedTweetSetter, MongoDAO):
    """
    An abstract class representing an object that stores tweets in a
    datastore
    """

    def store_processed_tweet(self, processed_tweet, check=True):
        if check:
            if self._contains_processed_tweet(processed_tweet):
                pass
            else:
                self.collection.insert_one(processed_tweet.toDict())
        else:
            self.collection.insert_one(processed_tweet.toDict())

    def store_many_processed_tweets(self, processed_tweets, check=True):
        operations = []
        for processed_tweet in processed_tweets:
            if check and self._contains_processed_tweet(processed_tweet):
                pass
            else:
                operations.append(InsertOne(processed_tweet.toDict()))
                print('added!')
        print('waiting to update...')
        if len(operations) != 0:
            self.collection.bulk_write(operations)

    def _contains_processed_tweet(self, processed_tweet: ProcessedTweet) -> bool:
        return self.collection.find_one({"id": str(processed_tweet.id), "user_id": str(processed_tweet.user_id)}) is not None

    def get_ids_by_user(self, user_id) -> Set[str]:
        tweet_doc_list = self.collection.find({"user_id": str(user_id)})

        ids = []
        for doc in tweet_doc_list:
            ids.append(doc.get("user_id"))

        return set(ids)

    def contains_tweet(self, tweet: Tweet) -> bool:
        return self.collection.find_one({"id": str(tweet.id), "user_id": str(tweet.user_id)}) is not None
