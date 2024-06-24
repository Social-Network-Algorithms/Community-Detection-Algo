from src.model.tweet import Tweet
from src.model.user import User
from typing import Dict, List, Tuple


class BlueSkyGetter():
    def get_tweets_by_user_id(self, user_id: str, num_tweets=0, start_date=None, end_date=None):
        raise NotImplementedError("Subclasses should implement this")

    def get_user_by_id(self, user_id: str) -> User:
        raise NotImplementedError("Subclasses should implement this")

    def get_user_by_screen_name(self, screen_name: str) -> User:
        raise NotImplementedError("Subclasses should implement this")

    def get_friends_ids_by_user_id(self, user_id: str, num_friends=0) -> Tuple[str, List[str]]:
        raise NotImplementedError("Subclasses should implement this")

    def get_friends_users_by_user_id(self, user_id: str, num_friends=0) -> Tuple[str, List[User]]:
        raise NotImplementedError("Subclasses should implement this")

    def get_followers_ids_by_user_id(self, user_id: str, num_followers=0) -> Tuple[str, List[str]]:
        raise NotImplementedError("Subclasses should implement this")

    def get_followers_users_by_user_id(self, user_id: str, num_followers=0) -> Tuple[str, List[User]]:
        raise NotImplementedError("Subclasses should implement this")

    def get_users_by_user_id_list(self, user_id_list: List[str]) -> List[User]:
        return [self.get_user_by_id(user_id) for user_id in user_id_list]

    def get_tweets_by_screen_name(self, screen_name: str, num_tweets=0):
        user = self.get_user_by_screen_name(screen_name)
        return self.get_tweets_by_user_id(user.id)

    def get_friends_ids_by_screen_name(self, screen_name: str, num_friends=0) -> Tuple[str, List[str]]:
        user = self.get_user_by_screen_name(screen_name)
        return self.get_friends_ids_by_user_id(user.id, num_friends=num_friends)

    def get_followers_ids_by_screen_name(self, screen_name: str, num_followers=0) -> Tuple[str, List[str]]:
        user = self.get_user_by_screen_name(screen_name)
        return self.get_followers_ids_by_user_id(user.id, num_followers=num_followers)

    def get_friends_users_by_screen_name(self, screen_name: str, num_friends=0) -> Tuple[str, List[User]]:
        user = self.get_user_by_screen_name(screen_name)
        return self.get_friends_users_by_user_id(user.id, num_friends=num_friends)

    def get_followers_users_by_screen_name(self, screen_name: str, num_followers=0) -> Tuple[str, List[User]]:
        user = self.get_user_by_screen_name(screen_name)
        return self.get_followers_users_by_user_id(user.id, num_followers=num_followers)

    def get_random_tweet(self) -> Tweet:
        raise NotImplementedError("Subclasses should implement this")

