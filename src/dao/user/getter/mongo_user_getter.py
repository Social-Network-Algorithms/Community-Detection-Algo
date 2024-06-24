from typing import List, Dict
from src.model.user import User
from src.dao.user.getter.user_getter import UserGetter
import src.dependencies.injector as sdi
from src.shared.utils import get_project_root

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

class MongoUserGetter(UserGetter):
    def __init__(self):
        self.user_collection = None

    def set_user_collection(self, user_collection: str) -> None:
        self.user_collection = user_collection

    def get_user_by_id(self, user_id: str) -> User:
        doc = self.user_collection.find_one({"id": str(user_id)})
        if doc is not None:
            return User.fromDict(doc)
        else:
            injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
            dao_module = injector.get_dao_module()
            bluesky_getter = dao_module.get_bluesky_getter()
            user_setter = dao_module.get_user_setter()
            user = bluesky_getter.get_user_by_id(user_id)
            if user is not None:
                user_setter.store_user(user)
            return user

    def get_user_by_screen_name(self, screen_name: str) -> User:
        return User.fromDict(self.user_collection.find_one({"screen_name": screen_name}))
    
    # Get all users
    def get_all_users(self) -> List[User]:
        return [doc["id"] for doc in self.user_collection.find()]
