from typing import Dict, List


class CommunitySetter:
    def store_community(self, iteration: int, added_users: List, current_community: List):
        raise NotImplementedError("Subclasses should implement this")