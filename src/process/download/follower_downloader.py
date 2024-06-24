class BlueskyFollowerDownloader():
    """
    Download Bluesky Followers for use in future algorithms.
    """

    def __init__(self, tweepy_getter, user_follower_setter, user_setter):
        self.bluesky_getter = tweepy_getter
        self.user_follower_setter = user_follower_setter
        self.user_setter = user_setter

    def download_followers_ids_by_id(self, user_id: str, num_followers=None) -> None:
        """
        """
        id, followers_user_ids = self.bluesky_getter.get_followers_ids_by_user_id(user_id, num_followers)
        self.user_follower_setter.store_followers(id, followers_user_ids)

    def download_followers_ids_by_screen_name(self, screen_name: str, num_followers=None) -> None:
        """
        """
        user_id = self.bluesky_getter.get_user_by_screen_name(screen_name).id
        id, followers_user_ids = self.bluesky_getter.get_followers_ids_by_user_id(user_id, num_followers)
        self.user_follower_setter.store_followers(id, followers_user_ids)

    def download_followers_users_by_id(self, user_id: str, num_followers=None) -> None:
        """
        Gets a list of followers of a user by id

        @param user_id the id of the user to query on
        @param num_followers the maximum number of followers to retrieve

        @return a list of ids of followers for the given user
        """
        id, followers_users = self.bluesky_getter.get_followers_users_by_user_id(user_id, num_followers)

        self.user_setter.store_users(followers_users)

        follower_user_ids = [user.id for user in followers_users]
        self.user_follower_setter.store_followers(id, follower_user_ids)

    def download_followers_users_by_screen_name(self, screen_name: str, num_followers=None) -> None:
        """
        Gets a list of followers of a user by id

        @param screen_name the username of the user to query on
        @param num_followers the maximum number of followers to retrieve

        @return a list of ids of followers for the given user
        """
        user_id = self.bluesky_getter.get_user_by_screen_name(screen_name).id
        id, followers_users = self.bluesky_getter.get_followers_users_by_user_id(user_id, num_followers)

        self.user_setter.store_users(followers_users)

        follower_user_ids = [user.id for user in followers_users]
        self.user_follower_setter.store_followers(id, follower_user_ids)
