import logging
from time import sleep

from atproto_client import SessionEvent, Session
from atproto_firehose import FirehoseSubscribeLabelsClient, parse_subscribe_labels_message
from click.core import batch

import conf.credentials as credentials
from typing import Union, List, Dict, Tuple, Optional
from src.model.tweet import Tweet
from src.model.user import User
from src.dao.bluesky.bluesky_dao import BlueSkyGetter
from src.shared.logger_factory import LoggerFactory
import threading
from atproto import Client

log = LoggerFactory.logger(__name__)

apiThreadLock = threading.Lock()


class BlueSkyAuthenticator():
    client = Client()

    def login(self):
        logging.getLogger("httpx").setLevel(logging.WARNING)
        self.client.on_session_change(self.on_session_change)

        session_string = self.get_session()
        if session_string:
            # print('Reusing session')
            try:
                self.client.login(session_string=session_string)
            except Exception as e:
                sleep(60)
                self.client.login(session_string=session_string)
        else:
            # print('Creating new session')
            self.client.login(credentials.USER_NAME, credentials.PASSWORD)
        return self.client

    def get_session(self) -> Optional[str]:
        try:
            with open('session.txt') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def save_session(self, session_string: str) -> None:
        with open('session.txt', 'w') as f:
            f.write(session_string)

    def on_session_change(self, event: SessionEvent, session: Session) -> None:
        if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
            self.save_session(session.export())


class TweepyBlueSkyGetter(BlueSkyGetter):
    def __init__(self):
        self.client = BlueSkyAuthenticator().login()

    def get_user_by_id(self, user_id: str) -> User:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        params = {'actor': user_id}
        at_user = None
        try:
            at_user = self.client.app.bsky.actor.get_profile(params=params)
        except Exception as e:
            pass

        if at_user is not None:
            user = User.fromATprotoObject(at_user)
            return user

        return None

    def get_user_by_screen_name(self, screen_name: str) -> User:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        params = {'actor': screen_name}
        at_user = None
        try:
            at_user = self.client.app.bsky.actor.get_profile(params=params)
        except Exception as e:
            pass

        if at_user is not None:
            user = User.fromATprotoObject(at_user)
            return user

        return None

    def get_tweets_by_user_id(self, user_id, num_tweets=0, start_date=None, end_date=None):
        logging.getLogger("httpx").setLevel(logging.WARNING)
        tweets = []
        has_more = True
        params = {'actor': user_id, 'filter': 'posts_and_author_threads', 'cursor': '', 'limit': 100}
        try:
            while has_more:
                if num_tweets is not None and len(tweets) >= num_tweets:
                    break

                response = self.client.app.bsky.feed.get_author_feed(params=params)
                response_posts_list = response["feed"]
                for post in response_posts_list:
                    tweets.append(Tweet.fromATprotoToObject(post["post"], post["reason"]))

                if response["cursor"] is not None:
                    params["cursor"] = response["cursor"]
                else:
                    has_more = False

        except Exception as e:
            log.error(e)

        def pred(tweet):
            is_correct_date = start_date <= tweet.created_at < end_date
            is_correct_user = tweet.user_id == id or tweet.user_name == id
            return is_correct_date and is_correct_user

        return list(filter(pred, tweets)) if start_date and end_date else list(tweets)

    def get_friends_ids_by_user_id(self, user_id: str, num_friends=0) -> Tuple[str, List[str]]:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        friends_user_ids = []
        params = {'actor': user_id, 'cursor': '', 'limit': 100}
        has_more = True
        try:
            while has_more:
                if num_friends is not None and len(friends_user_ids) >= num_friends:
                    break

                response = self.client.app.bsky.graph.get_follows(params=params)
                response_friends_list = response["follows"]
                for friend in response_friends_list:
                    friends_user_ids.append(friend.did)

                if response["cursor"] is not None:
                    params["cursor"] = response["cursor"]
                else:
                    has_more = False

        except Exception as ex:
            log.error("Could not download friends ids")
        return user_id, friends_user_ids

    def get_friends_users_by_user_id(self, user_id: str, num_friends=0) -> Tuple[str, List[User]]:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        """
        @param user_id id of the user to get friends for
        @param num_friends: 0 means ALL friends, based on tweepy.Cursor.items()
        """
        friends_users = []
        count = 0
        params = {'actor': user_id, 'cursor': '', 'limit': 100}
        has_more = True

        try:
            while has_more:
                if num_friends is not None and len(friends_users) >= num_friends:
                    break

                response = self.client.app.bsky.graph.get_follows(params=params)
                response_friends_list = response["follows"]
                for friend in response_friends_list:
                    count += 1
                    friend_user = self.get_user_by_id(friend.did)
                    log.info("Downloaded user " + str(friend.did))
                    friends_users.append(friend_user)

                if response["cursor"] is not None:
                    params["cursor"] = response["cursor"]
                else:
                    has_more = False
            log.info(f"total friends {count}")
        except Exception as e:
            log.error("error occurs")

        return user_id, friends_users

    def get_followers_ids_by_user_id(self, user_id: str, num_followers=0) -> Tuple[str, List[str]]:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        followers_user_ids = []
        params = {'actor': user_id, 'cursor': '', 'limit': 100}

        has_more = True
        try:
            while has_more:
                if num_followers is not None and len(followers_user_ids) >= num_followers:
                    break

                response = self.client.app.bsky.graph.get_followers(params=params)
                response_followers_list = response["followers"]

                for follower in response_followers_list:
                    followers_user_ids.append(follower.did)

                if response["cursor"] is not None:
                    params["cursor"] = response["cursor"]
                else:
                    has_more = False

        except Exception as ex:
            log.error("Could not download followe ids")

        return user_id, followers_user_ids

    def get_followers_users_by_user_id(self, user_id: str, num_followers=0) -> Tuple[str, List[User]]:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        followers_users = []
        count = 0
        params = {'actor': user_id, 'cursor': '', 'limit': 100}
        has_more = True

        try:
            while has_more:
                if num_followers is not None and len(followers_users) >= num_followers:
                    break

                response = self.client.app.bsky.graph.get_followers(params=params)
                response_followers_list = response["followers"]
                for follower in response_followers_list:
                    count += 1
                    friend_user = self.get_user_by_id(follower.did)
                    log.info("Downloaded user " + str(follower.did))
                    followers_users.append(friend_user)

                if response["cursor"] is not None:
                    params["cursor"] = response["cursor"]
                else:
                    has_more = False
            log.info(f"total friends {count}")
        except Exception as e:
            log.error("error occurs")

        return user_id, followers_users

    def get_random_tweet(self) -> Tweet:
        stream_client = FirehoseSubscribeLabelsClient()
        random_tweets_ids = []

        def on_message_handler(message) -> None:
            if len(random_tweets_ids) < 1:
                labels_message = parse_subscribe_labels_message(message)
                random_tweets_ids.append(labels_message.labels[0].uri)
                stream_client.stop()

        stream_client.start(on_message_handler)

        if len(random_tweets_ids) != 0:
            response = self.client.get_posts(uris=[random_tweets_ids[0]])
            post_info = response["posts"][0]
            random_post = Tweet.fromATprotoToObject(post_info, None)
        else:
            random_post = None

        return random_post

    def get_users_relationships(self, user_id_1: str, user_list) -> dict:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        relationships_dict = {}
        for x in batch(user_list, 30):
            params = {'actor': user_id_1, 'others': list(x)}
            try:
                response = self.client.app.bsky.graph.get_relationships(params=params)
                relationships = response["relationships"]
                for relationship in relationships:
                    user = relationship["did"]
                    relationships_dict[user] = [0, 0]
                    if relationship["followed_by"] is not None:
                        relationships_dict[user][0] = 1
                    if relationship["following"] is not None:
                        relationships_dict[user][1] = 1
            except Exception as e:
                pass

        return relationships_dict
