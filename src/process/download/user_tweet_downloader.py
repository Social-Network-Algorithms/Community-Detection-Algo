from typing import Union, List

from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.model.tweet import Tweet
from src.model.user import User
from src.dao.twitter.twitter_dao import TwitterGetter
from src.dao.user.getter.user_getter import UserGetter
from src.dao.raw_tweet.setter.raw_tweet_setter import RawTweetSetter
from src.shared.logger_factory import LoggerFactory
from typing import Optional
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta

log = LoggerFactory.logger(__name__)


class UserTweetDownloader():
    """
    Downloads tweets for a particular user
    """

    def __init__(self, twitter_getter: TwitterGetter, user_tweets_getter: UserTweetsGetter, user_tweets_setter: UserTweetsSetter,
                 user_getter: Optional[UserGetter] = None):
        self.twitter_getter = twitter_getter
        self.user_tweets_getter = user_tweets_getter
        self.user_tweets_setter = user_tweets_setter
        self.user_getter = user_getter

    def download_user_tweets_by_user(self, user: User, months_back=12) -> None:
        self.download_user_tweets_by_screen_name(user.screen_name, months_back)

    def download_user_tweets_by_screen_name(self, screen_name: str, months_back=24) -> None:
        """
        @param months_back: the number of months we are going to count back from the current date,
        to get a new past date as our start date for downloading tweets. Any older tweets are ignored.
        """
        user_id = self.user_getter.get_user_by_screen_name(screen_name).id
        all_tweets = self.twitter_getter.get_tweets_by_user_id(user_id)
        tweets = []
        startDate = date.today() + relativedelta(months=-months_back)
        for tweet in all_tweets:
            createDate_str = tweet.created_at[:10]
            createDate = datetime.strptime(createDate_str, '%Y-%m-%d')
            if createDate.date() > startDate:
                tweets.append(tweet)
        self.user_tweets_setter.store_tweets(user_id, tweets)
        log.info(f"Downloaded {len(tweets)} Tweets for user {screen_name}")

    def download_user_tweets_by_user_id(self, user_id: str, months_back=12) -> None:
        """
        @param months_back: the number of months we are going to count back from the current date,
        to get a new past date as our start date for downloading tweets. Any older tweets are ignored.
        """
        all_tweets = self.twitter_getter.get_tweets_by_user_id(user_id)
        tweets = []
        startDate = date.today() + relativedelta(months=-months_back)

        for tweet in all_tweets:
            createDate_str = tweet.created_at[:10]
            createDate = datetime.strptime(createDate_str, '%Y-%m-%d')
            if createDate.date() > startDate:
                tweets.append(tweet)
        self.user_tweets_setter.store_tweets(user_id, tweets)
        log.info(f"Downloaded {len(tweets)} Tweets for user {user_id}")

    def download_user_tweets_by_user_list(self, user_ids: List[str], months_back=12):
        num_ids = len(user_ids)
        count = 0
        for id in user_ids:
            # user = self.user_getter.get_user_by_id(id)
            # tweet_count = self.raw_tweet_setter.get_num_user_tweets(id)
            #
            # if tweet_count >= 10:
            #     log.info("Skipping " + str(id))
            # else:
            self.download_user_tweets_by_user_id(id, months_back)
            count += 1

            log.log_progress(log, count, num_ids)

        log.info("Done downloading for user list")

    def stream_tweets_by_user_list(self, user_ids: List[str]):
        modified_list = []
        if self.user_getter is not None:
            log.info("Checking Users")
            for user_id in user_ids:
                # user = self.user_getter.get_user_by_id(user_id)
                # Number of user tweets
                count = len(self.user_tweets_getter.get_user_tweets(user_id))

                # if count >= 3000 or (user is not None and user.statuses_count <= count):
                if count >= 10:
                    log.info("Skipping " + str(user_id))
                else:
                    modified_list.append(user_id)
        log.info("Starting Download")

        for user_id in modified_list:
            tweets = self.twitter_getter.get_tweets_by_user_id(user_id, 500)
            self.user_tweets_setter.store_tweets(user_id, tweets)
