import time
import functools
import datetime
from typing import Union, List

from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.dao.twitter.twitter_dao import TwitterGetter


class TwitterTweetDownloader():
    """
    Downloads a twitter tweet downloader
    """

    def __init__(self, twitter_getter: TwitterGetter, user_tweets_setter: UserTweetsSetter):
        self.twitter_getter = twitter_getter
        self.user_tweets_setter = user_tweets_setter

    def get_random_tweet(self):
        random_tweet = self.twitter_getter.get_random_tweet()
        self.user_tweets_setter.store_tweets(random_tweet.user_id, random_tweet)
