from src.dao.user_tweets.getter.mongo_user_tweets_getter import MongoUserTweetsGetter
from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dao.user_tweets.setter.mongo_user_tweets_setter import MongoUserTweetsSetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.shared.mongo import get_collection_from_config
from typing import Dict


class UserTweetsDAOFactory():
    def create_setter(tweets: Dict) -> UserTweetsSetter:
        user_tweets_setter = None
        if tweets["type"] == "Mongo":
            user_tweets_setter = MongoUserTweetsSetter()
            collection = get_collection_from_config(tweets["config"])
            user_tweets_setter.set_user_tweets_collection(collection)
        else:
            raise Exception("Datastore type not supported")

        return user_tweets_setter

    def create_getter(tweets: Dict) -> UserTweetsGetter:
        user_tweets_getter = None
        if tweets["type"] == "Mongo":
            user_tweets_getter = MongoUserTweetsGetter()
            collection = get_collection_from_config(tweets["config"])
            user_tweets_getter.set_user_tweets_collection(collection)
        else:
            raise Exception("Datastore type not supported")

        return user_tweets_getter
