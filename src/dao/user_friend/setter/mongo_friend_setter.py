from typing import List, Dict
from src.dao.user_friend.setter.friend_setter import FriendSetter


class MongoFriendSetter(FriendSetter):
    def __init__(self):
        self.friend_collection = None

    def set_friend_collection(self, friend_collection: str) -> None:
        self.friend_collection = friend_collection

    def store_friends(self, user_id: str, friends_ids: List[str]):
        doc = {"user_id": str(user_id), "friends_ids": friends_ids}

        if self.contains_user(user_id):
            self.friend_collection.find_one_and_replace({"user_id": str(user_id)}, doc)
        else:
            self.friend_collection.insert_one(doc)

    def contains_user(self, user_id: str) -> bool:
        return self.friend_collection.find_one({"user_id": str(user_id)}) is not None
