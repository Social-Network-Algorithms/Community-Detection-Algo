from src.dao.retweeted_users.setter.retweet_users_setter import RetweetUsersSetter
from src.dao.bluesky.bluesky_dao import BlueSkyGetter
from src.dao.user_friend.setter.friend_setter import FriendSetter
from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.download.user_downloader import BlueskyUserDownloader
from src.dao.user.getter.user_getter import UserGetter
from src.dao.user_activity.getter.user_activity_getter import ActivityGetter
from src.dao.user_friend.getter.friend_getter import FriendGetter
from src.dao.local_neighbourhood.setter.local_neighbourhood_setter import LocalNeighbourhoodSetter
from src.model.local_neighbourhood import LocalNeighbourhood

from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)


class LocalNeighbourhoodDownloader():
    def __init__(self, bluesky_getter: BlueSkyGetter,
                 user_downloader: BlueskyUserDownloader,
                 user_getter: UserGetter,
                 user_friend_getter: FriendGetter,
                 user_activity_getter: ActivityGetter,
                 user_friend_setter: FriendSetter,
                 user_tweets_getter: UserTweetsGetter,
                 retweeted_user_setter: RetweetUsersSetter,
                 local_neighbourhood_setter: LocalNeighbourhoodSetter,
                 user_activity: str):
        self.bluesky_getter = bluesky_getter
        self.user_downloader = user_downloader
        self.user_friend_getter = user_friend_getter
        self.user_getter = user_getter
        self.user_activity_getter = user_activity_getter
        self.user_friend_setter = user_friend_setter
        self.user_tweets_getter = user_tweets_getter
        self.retweeted_user_setter = retweeted_user_setter
        self.local_neighbourhood_setter = local_neighbourhood_setter
        self.user_activity = user_activity

    def download_local_neighbourhood_by_id(self, user_id: str, params=None, clean=True):
        user_friends_ids = self.user_friend_getter.get_user_friends_ids(
            user_id)
        if user_friends_ids is None:
            # Download and store user friends if missing
            _, user_friends_ids_ = self.bluesky_getter.get_friends_ids_by_user_id(user_id, None)
            self.user_friend_setter.store_friends(user_id, user_friends_ids_)
            user_friends_ids = self.user_friend_getter.get_user_friends_ids(
                user_id)
        assert user_friends_ids is not None

        log.info(f"Downloading local neighbourhood of {user_id}")
        log.info(f"{user_id} has {len(user_friends_ids)} friends")
        t = None
        if clean:
            user_friends_ids, t = self.clean_user_friends_global(
                user_id, user_friends_ids)

        user_dict = {}
        # Append user_id to user_friends_ids
        user_friends_ids.append(user_id)

        num_ids = len(user_friends_ids)
        log.info(f"Cleaning Threshold: {t}")
        log.info("Starting Downloading Friend List for " +
                 str(len(user_friends_ids)) + " users")
        for i in range(num_ids):
            id = user_friends_ids[i]
            user_activities = self.user_activity_getter.get_user_activities(id)

            if user_activities is None:
                # download user activities
                if self.user_activity == 'friends':
                    # download the friends of the friend
                    _, friend_friend_ids = self.bluesky_getter.get_friends_ids_by_user_id(id, None)
                    self.user_friend_setter.store_friends(id, friend_friend_ids)
                    user_activities = self.user_activity_getter.get_user_activities(id)

                elif self.user_activity == "user retweets":
                    # download the original user retweets of the friend
                    all_tweets = self.user_tweets_getter.get_user_tweets(id)
                    retweeted_users = [tweet.retweet_user_id for tweet in all_tweets if tweet.retweet_user_id is not None]
                    self.retweeted_user_setter.store_retweet_users(id, retweeted_users)
                    user_activities = self.user_activity_getter.get_user_activities(id)

            assert user_activities is not None

            if self.user_activity == 'friends':
                user_dict[str(id)] = [str(id)
                                      for id in user_activities if id in user_friends_ids]
            else:
                user_dict[str(id)] = [str(id)
                                      for id in user_activities]

            log.log_progress(log, i, num_ids)

        local_neighbourhood = LocalNeighbourhood(
            seed_id=user_id, params=params, users=user_dict, user_activity=self.user_activity)
        self.local_neighbourhood_setter.store_local_neighbourhood(
            local_neighbourhood)

        log.info("Done downloading local neighbourhood")

    def download_local_neighbourhood_by_screen_name(self, screen_name: str, params=None):
        log.info("Downloading local neighbourhood of " + str(screen_name))

        self.user_downloader.download_user_by_screen_name(screen_name)
        id = self.user_getter.get_user_by_screen_name(screen_name).get_id()

        self.download_local_neighbourhood_by_id(id, params)

    def clean_user_friends_global(self, user_id, friends_list):
        user = self.user_getter.get_user_by_id(str(user_id))
        log.info("Cleaning Friends List by Follower and Friend")
        t = 0.05

        num_users = len(friends_list)
        clean_friends_list = friends_list
        while num_users > 250:
            num_users = len(friends_list)
            clean_friends_list = []
            follower_thresh = t * user.followers_count
            if user.friends_count < 0.2 * user.followers_count:
                friend_thresh = t * user.friends_count
            else:
                friend_thresh = t * 0.2 * user.friends_count
            print(
                f"Data cleaning with thresholds {follower_thresh, friend_thresh}")
            for id in friends_list:
                num_users -= 1
                curr_user = self.user_getter.get_user_by_id(id)
                if user is not None and curr_user is not None and curr_user.followers_count > follower_thresh and curr_user.friends_count > friend_thresh:
                    clean_friends_list.append(id)
                    num_users += 1
            log.info(
                f"Increasing Data Cleaning Strength {t}, {num_users} remaining users")
            t += 0.025
        return clean_friends_list, t
