from src.model.user import User
from src.dao.user.setter.user_setter import UserSetter


class MongoUserSetter(UserSetter):
    def __init__(self):
        self.user_collection = None

    def set_user_collection(self, user_collection: str) -> None:
        self.user_collection = user_collection

    def store_user(self, user: User) -> None:
        doc = user.__dict__

        if self.contains_user(user.id):
            self.user_collection.find_one_and_replace({"id": str(user.id)}, doc)
        else:
            self.user_collection.insert_one(doc)

    def contains_user(self, user_id: str) -> bool:
        return self.user_collection.find_one({"id": str(user_id)}) is not None
