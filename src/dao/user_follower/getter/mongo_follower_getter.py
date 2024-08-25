from typing import List, Dict

from src.dao.user_follower.getter.follower_getter import FollowerGetter
import src.dependencies.injector as sdi
from src.shared.utils import get_project_root

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


class MongoFollowerGetter(FollowerGetter):
    def __init__(self):
        self.follower_collection = None

    def set_follower_collection(self, follower_collection: str) -> None:
        self.follower_collection = follower_collection

    def download_missing_followers(self, user_id: str, count=None):
        injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
        dao_module = injector.get_dao_module()
        bluesky_getter = dao_module.get_bluesky_getter()
        follower_setter = dao_module.get_user_follower_setter()
        _, followers_user_ids = bluesky_getter.get_followers_ids_by_user_id(user_id, count)
        follower_setter.store_followers(user_id, followers_user_ids)

    def get_user_follower_ids(self, user_id: str, count=None) -> List[str]:
        """Given a user id, return the ids of friends"""
        doc = self.follower_collection.find_one({"user_id":str(user_id)})
        if doc is None:
            self.download_missing_followers(user_id, count)
            doc = self.follower_collection.find_one({"user_id":str(user_id)})

        return doc["follower_ids"]

    def contains_user(self, user_id: str) -> bool:
        return self.follower_collection.find_one({"user_id": str(user_id)}) is not None
