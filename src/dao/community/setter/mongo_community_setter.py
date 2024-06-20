from src.dao.community.setter.community_setter import CommunitySetter
from typing import List


class MongoCommunitySetter(CommunitySetter):
    def __init__(self):
        self.collection = None

    def set_collection(self, collection) -> None:
        self.collection = collection

    def store_community(self, iteration: int, added_users: List, current_community: List):
        if self._contains_community(current_community, added_users):
            pass
        else:
            doc = {"iteration": iteration,
                "added_users": added_users,
                "current_community": current_community}
            self.collection.insert_one(doc)

    def _contains_community(self, current_community, added_users):
        return self.collection.find_one({"current_community": current_community, "added_users": added_users}) is not None