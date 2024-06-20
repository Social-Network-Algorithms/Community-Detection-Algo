from src.dao.processed_tweet.getter.processed_tweet_getter import ProcessedTweetGetter
from src.dao.mongo.mongo_dao import MongoDAO
from src.model.processed_tweet import ProcessedTweet


class MongoProcessedTweetGetter(ProcessedTweetGetter, MongoDAO):
    def __init__(self):
        self.collection = None

    def set_collection(self, collection) -> None:
        self.collection = collection

    def get_user_processed_tweets(self, user_id: str):
        tweet_doc_list = self.collection.find({"user_id": str(user_id)})

        tweets = []
        for doc in tweet_doc_list:
            tweets.append(ProcessedTweet.fromDict(doc))

        return tweets
