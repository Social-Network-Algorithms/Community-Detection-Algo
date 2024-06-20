from src.dao.user_processed_tweets.getter.mongo_user_processed_tweets_getter import MongoUserProcessedTweetsGetter
from src.dao.user_processed_tweets.getter.user_processed_tweets_getter import UserProcessedTweetsGetter
from src.dao.user_processed_tweets.setter.mongo_user_processed_tweets_setter import MongoUserProcessedTweetsSetter
from src.dao.user_processed_tweets.setter.user_processed_tweets_setter import UserProcessedTweetsSetter
from src.shared.mongo import get_collection_from_config
from typing import Dict


class UserProcessedTweetsDAOFactory():
    def create_setter(tweets: Dict) -> UserProcessedTweetsSetter:
        user_processed_tweets_setter = None
        if tweets["type"] == "Mongo":
            user_processed_tweets_setter = MongoUserProcessedTweetsSetter()
            collection = get_collection_from_config(tweets["config"])
            user_processed_tweets_setter.set_user_tweets_collection(collection)
        else:
            raise Exception("Datastore type not supported")

        return user_processed_tweets_setter

    def create_getter(tweets: Dict) -> UserProcessedTweetsGetter:
        user_processed_tweets_getter = None
        if tweets["type"] == "Mongo":
            user_processed_tweets_setter = MongoUserProcessedTweetsGetter()
            collection = get_collection_from_config(tweets["config"])
            user_processed_tweets_setter.set_user_tweets_collection(collection)
        else:
            raise Exception("Datastore type not supported")

        return user_processed_tweets_setter
