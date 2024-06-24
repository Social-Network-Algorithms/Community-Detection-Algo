from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

class FriendDownloader():
    """
    Download Bluesky Followers for use in future algorithms.
    """

    def __init__(self, bluesky_getter, user_friend_getter, user_friend_setter, user_setter, user_getter):
        self.bluesky_getter = bluesky_getter
        self.user_friend_getter = user_friend_getter
        self.user_friend_setter = user_friend_setter
        self.user_setter = user_setter
        self.user_getter = user_getter

    def download_friends_ids_by_id(self, user_id: str, num_friends=0) -> None:
        """
        Gets a list of friends ids of a user by id
        """
        if not self.user_friend_getter.contains_user(user_id):
            id, friends_user_ids = self.bluesky_getter.get_friends_ids_by_user_id(user_id, num_friends=num_friends)
            self.user_friend_setter.store_friends(id, friends_user_ids)

    def download_friends_ids_by_screen_name(self, screen_name: str, num_friends=0) -> None:
        """
        """
        #if not self.user_friend_getter.contains_user(user_id):
        id, friends_user_ids = self.bluesky_getter.get_friends_ids_by_screen_name(screen_name, num_friends=num_friends)
        self.user_friend_setter.store_friends(id, friends_user_ids)

    def download_friends_users_by_id(self, user_id: str, num_friends=0) -> None:
        """
        Gets a list of friends of a user by id

        @param user_id the id of the user to query on
        @param num_friends the maximum number of friends to retrieve

        @return a list of users who are friends of the given user
        """
        try:
            # Check if all users have been downloaded
            assert self.user_friend_getter.contains_user(user_id)
            friends_users_ids = self.user_friend_getter.get_user_friends_ids(user_id)
            assert friends_users_ids is not None
            assert len(friends_users_ids) >= self.user_getter.get_user_by_id(user_id).friends_count

            for id in friends_users_ids:
                assert self.user_setter.contains_user(id)
            log.info("Skipping user friends download, since all users have been downloaded")
        except Exception as e:
            log.info("Downloading user friends for user " + str(user_id))
            id, friends_users = self.bluesky_getter.get_friends_users_by_user_id(user_id, num_friends=num_friends)

            self.user_setter.store_users(friends_users)

            friend_user_ids = [user.id for user in friends_users]
            self.user_friend_setter.store_friends(str(user_id), friend_user_ids)


    def download_friends_users_by_screen_name(self, screen_name: str, num_friends=0) -> None:
        """
        Gets a list of friends of a user by id

        @param user_id the id of the user to query on
        @param num_friends the maximum number of friends to retrieve

        @return a list of ids of friends for the given user
        """
        id, friends_users = self.bluesky_getter.get_friends_users_by_screen_name(screen_name, num_friends=num_friends)

        self.user_setter.store_users(friends_users)

        friend_user_ids = [user.id for user in friends_users]
        self.user_friend_setter.store_friends(id, friend_user_ids)
