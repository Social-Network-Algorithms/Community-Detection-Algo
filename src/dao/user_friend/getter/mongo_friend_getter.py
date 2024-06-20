from typing import List, Dict
from src.dao.user_friend.getter.friend_getter import FriendGetter


class MongoFriendGetter(FriendGetter):
    def __init__(self):
        self.friend_collection = None

    def set_friend_collection(self, friend_collection: str) -> None:
        self.friend_collection = friend_collection

    def get_user_friends_ids(self, user_id: str) -> List[str]:
        """Given a user id, return the ids of friends"""
        doc = self.friend_collection.find_one({"user_id":str(user_id)})
        if doc is not None:
            return doc["friends_ids"]
        else:
            return None

    def contains_user(self, user_id: str) -> bool:
        return self.friend_collection.find_one({"user_id": str(user_id)}) is not None
