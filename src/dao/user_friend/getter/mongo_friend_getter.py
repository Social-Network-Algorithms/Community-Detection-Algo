from typing import List, Dict
from src.dao.user_friend.getter.friend_getter import FriendGetter
import src.dependencies.injector as sdi
from src.shared.utils import get_project_root

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


class MongoFriendGetter(FriendGetter):
    def __init__(self):
        self.friend_collection = None

    def set_friend_collection(self, friend_collection: str) -> None:
        self.friend_collection = friend_collection

    def download_missing_friends(self, user_id: str, count=None):
        injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
        dao_module = injector.get_dao_module()
        bluesky_getter = dao_module.get_bluesky_getter()
        friends_setter = dao_module.get_user_friend_setter()
        _, friends_user_ids = bluesky_getter.get_friends_ids_by_user_id(user_id, count)
        friends_setter.store_friends(user_id, friends_user_ids)

    def get_user_friends_ids(self, user_id: str, count=None) -> List[str]:
        """Given a user id, return the ids of friends"""
        doc = self.friend_collection.find_one({"user_id":str(user_id)})
        if doc is None:
            self.download_missing_friends(user_id, count)
            doc = self.friend_collection.find_one({"user_id":str(user_id)})

        return doc["friends_ids"]

    def contains_user(self, user_id: str) -> bool:
        return self.friend_collection.find_one({"user_id": str(user_id)}) is not None
