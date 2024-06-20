from typing import List, Dict
from src.dao.user_follower.setter.follower_setter import FollowerSetter


class MongoFollowerSetter(FollowerSetter):
    def __init__(self):
        self.follower_collection = None

    def set_follower_collection(self, follower_collection: str) -> None:
        self.follower_collection = follower_collection

    def store_followers(self, user_id:str, follower_ids: List[str]):
        doc = { "user_id": user_id, "follower_ids": follower_ids }

        if self._contains_user(user_id):
            self.follower_collection.find_one_and_replace({"user_id": user_id}, doc)
        else:
            self.follower_collection.insert_one(doc)

    def _contains_user(self, user_id: str) -> bool:
        return self.follower_collection.find_one({"user_id": user_id}) is not None
