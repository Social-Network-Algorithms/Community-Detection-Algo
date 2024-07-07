from typing import List, Dict
from src.dao.retweeted_users.getter.retweet_users_getter import RetweetUsersGetter
import src.dependencies.injector as sdi
from src.shared.utils import get_project_root

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

class MongoRetweetUsersGetter(RetweetUsersGetter):
    def __init__(self):
        self.retweet_user_collection = None

    def set_retweet_user_collection(self, retweet_user_collection: str) -> None:
        self.retweet_user_collection = retweet_user_collection

    def download_missing_retweet_users(self, user_id: str):
        injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
        dao_module = injector.get_dao_module()
        bluesky_getter = dao_module.get_bluesky_getter()
        user_tweets_setter = dao_module.get_user_tweets_setter()
        retweeted_user_setter = dao_module.get_retweeted_users_setter()
        user_tweets = bluesky_getter.get_tweets_by_user_id(user_id, 600)
        user_tweets_setter.store_tweets(user_id, user_tweets)
        retweeted_users = [tweet.retweet_user_id for tweet in user_tweets if tweet.retweet_user_id is not None]
        retweeted_user_setter.store_retweet_users(user_id, retweeted_users)

    def get_retweet_users_ids(self, user_id: str) -> List[str]:
        doc = self.retweet_user_collection.find_one({"user_id": str(user_id)})
        if doc is None:
            self.download_missing_retweet_users(user_id)
            doc = self.retweet_user_collection.find_one({"user_id": str(user_id)})

        return doc["retweet_user_ids"]

    def contains_user(self, user_id: str) -> bool:
        return self.retweet_user_collection.find_one({"user_id": str(user_id)}) is not None
