from typing import List, Dict
from src.dao.retweeted_users.getter.retweet_users_getter import RetweetUsersGetter


class MongoRetweetUsersGetter(RetweetUsersGetter):
    def __init__(self):
        self.retweet_user_collection = None

    def set_retweet_user_collection(self, retweet_user_collection: str) -> None:
        self.retweet_user_collection = retweet_user_collection

    def get_retweet_users_ids(self, user_id: str) -> List[str]:
        doc = self.retweet_user_collection.find_one({"user_id": str(user_id)})
        if doc is not None:
            return doc["retweet_user_ids"]
        else:
            return None

    def contains_user(self, user_id: str) -> bool:
        return self.retweet_user_collection.find_one({"user_id": str(user_id)}) is not None
