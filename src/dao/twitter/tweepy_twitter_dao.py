import datetime
import conf.credentials as credentials
from typing import Union, List, Dict
from tweepy import OAuthHandler, Stream, API, Cursor
from tweepy.streaming import StreamListener
from src.model.tweet import Tweet
from src.model.user import User

class TweepyListener(StreamListener):
    def __init__(self, num_tweets, subscriber):
        super().__init__()

        self.counter = 0
        self.limit = num_tweets

        self.subscriber = subscriber

    def on_status(self, data):
        self.subscriber.on_status(data)
        self.counter += 1

        return self.counter <= self.limit

class TwitterAuthenticator():
    def authenticate(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY,
            credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN,
            credentials.ACCESS_TOKEN_SECRET)

        return auth

class TweepyTwitterGetter():
    def __init__(self):
        self.auth = TwitterAuthenticator().authenticate()
        self.twitter_api = API(self.auth, wait_on_rate_limit=True)

    def stream_tweets(self, num_tweets, subscriber) -> Tweet:
        """
        Creates a twitter stream, which downloads the given number of tweets.
        Each time a tweet is downloaded, the subscriber is notified (their
        on_status method is called)

        @param num_tweets the number of tweers to download
        @param subscriber the object to notify each time a tweet is downloaded
        """
        listener = TweepyListener(num_tweets=num_tweets, subscriber=subscriber)

        stream = Stream(self.auth, listener)
        stream.filter(languages=["en"])
        stream.sample()

    def get_user_by_id(self, user_id: str) -> User:
        tweepy_user = api.get_user(user_id=user_id)

        if tweepy_user is not None:
            user = User.fromTweepyJSON(tweepy_user._json)
            return user

        return None

    def get_user_by_user_id_list(self, user_id_list: List[str]) -> List[User]:
        return [self.get_user_by_id(user_id) for user_id in user_id_list]

    def get_user_by_screen_name(self, screen_name: str) -> User:
        tweepy_user = api.get_user(screen_name=screen_name)

        if tweepy_user is not None:
            user = User.fromTweepyJSON(tweepy_user._json)
            return user

        return None

    def get_friends_by_user(self, user: User, num_friends=0) -> List[User]:
        user_id = user.id
        friends_user_ids = [follower_id for follower_id in Cursor(self.twitter_api.friends_ids, user_id=user_id).items(limit=num_friends)]

        return friends_user_ids

    def get_followers_by_id(self, user: User, num_followers=0) -> List[User]:
        user_id = user.id
        followers_user_ids = [friend_id for friend_id in Cursor(self.twitter_api.followers_id, user_id=user_id).items(limit=num_friends)]

        return followers_user_ids
