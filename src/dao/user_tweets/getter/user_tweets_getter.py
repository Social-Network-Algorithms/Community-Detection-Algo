from typing import List, Dict

from src.model.tweet import Tweet


class UserTweetsGetter:
    def get_user_tweets(self, user_id: str) -> List[Tweet]:
        raise NotImplementedError("Subclasses should implement this")

    def get_tweets_by_user_ids(self, user_ids: List[str]) -> List[Tweet]:
        raise NotImplementedError("Subclasses should implement this")

    def get_tweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        raise NotImplementedError("Subclasses should implement this")

    def get_user_retweets(self, user_id: str) -> List[Tweet]:
        raise NotImplementedError("Subclasses should implement this")

    def get_retweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        raise NotImplementedError("Subclasses should implement this")

    def get_retweets_ids_by_user_id(self, user_id: str) -> List[str]:
        raise NotImplementedError("Subclasses should implement this")

    def get_all_tweets(self) -> List[Tweet]:
        raise NotImplementedError("Subclasses should implement this")

    def get_all_tweets_dict(self) -> Dict[str, List[Tweet]]:
        raise NotImplementedError("Subclasses should implement this")

    def get_all_retweets_dict(self) -> Dict[str, List[Tweet]]:
        raise NotImplementedError("Subclasses should implement this")

    def convert_dates(self):
        raise NotImplementedError("Subclasses should implement this")
