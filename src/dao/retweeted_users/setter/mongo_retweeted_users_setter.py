from typing import List, Dict
from src.dao.retweeted_users.setter.retweet_users_setter import RetweetUsersSetter


class MongoRetweetUsersSetter(RetweetUsersSetter):
    def __init__(self):
        self.retweet_users_collection = None

    def set_retweet_user_collection(self, retweet_users_collection: str) -> None:
        self.retweet_users_collection = retweet_users_collection

    def store_retweet_users(self, user_id: str, retweet_user_ids: List[str]):
        doc = {"user_id": str(user_id), "retweet_user_ids": retweet_user_ids}

        if self.contains_user(user_id):
            self.retweet_users_collection.find_one_and_replace({"user_id": str(user_id)}, doc)
        else:
            self.retweet_users_collection.insert_one(doc)

    def contains_user(self, user_id: str) -> bool:
        return self.retweet_users_collection.find_one({"user_id": str(user_id)}) is not None
