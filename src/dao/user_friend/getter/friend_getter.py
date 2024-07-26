from typing import List
from src.model.user import User


class FriendGetter:
    def get_user_friends_ids(self, user_id: str, count=None) -> List[str]:
        raise NotImplementedError("Subclasses should implement this")
