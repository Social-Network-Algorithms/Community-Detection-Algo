from src.dao.user_follower.getter.follower_getter import FollowerGetter
from src.dao.user_follower.getter.mongo_follower_getter import MongoFollowerGetter
from src.dao.user_follower.setter.follower_setter import FollowerSetter
from src.dao.user_follower.setter.mongo_follower_setter import MongoFollowerSetter
from src.shared.mongo import get_collection_from_config
from typing import Dict

class UserFollowerDAOFactory():
    def create_setter(followers: Dict) -> FollowerSetter:
        follower_setter = None
        if followers["type"] == "Mongo":
            follower_setter = MongoFollowerSetter()
            collection = get_collection_from_config(followers["config"])
            follower_setter.set_follower_collection(collection)
        else:
            raise Exception("Datastore type not supported")

        return follower_setter

    def create_getter(followers: Dict) -> FollowerGetter:
        follower_getter = None
        if followers["type"] == "Mongo":
            follower_getter = MongoFollowerGetter()
            collection = get_collection_from_config(followers["config"])
            follower_getter.set_follower_collection(collection)
        else:
            raise Exception("Datastore type not supported")

        return follower_getter
