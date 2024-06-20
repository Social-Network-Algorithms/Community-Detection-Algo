from typing import List


class RetweetUsersGetter:
    def get_retweet_users_ids(self, user_id: str) -> List[str]:
        raise NotImplementedError("Subclasses should implement this")
