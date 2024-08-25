from typing import List


class FollowerGetter:
    def get_user_follower_ids(self, user_id: str, count=None) -> List[str]:
        raise NotImplementedError("Subclasses should implement this")
