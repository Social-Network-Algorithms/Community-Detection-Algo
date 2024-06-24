import time
import functools
import datetime
from typing import Union, List

from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.dao.bluesky.bluesky_dao import BlueSkyGetter


class BlueskyTweetDownloader():
    """
    Downloads a bluesky tweet downloader
    """

    def __init__(self, bluesky_getter: BlueSkyGetter, user_tweets_setter: UserTweetsSetter):
        self.bluesky_getter = bluesky_getter
        self.user_tweets_setter = user_tweets_setter

    def get_random_tweet(self):
        random_tweet = self.bluesky_getter.get_random_tweet()
        self.user_tweets_setter.store_tweets(random_tweet.user_id, [random_tweet])
