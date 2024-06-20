from atproto_client import SessionEvent, Session
from atproto_firehose import FirehoseSubscribeLabelsClient, parse_subscribe_labels_message

import conf.credentials as credentials
from typing import Union, List, Dict, Tuple, Optional
from src.model.tweet import Tweet
from src.model.user import User
from src.dao.twitter.twitter_dao import TwitterGetter
from tweepy import TweepError
from src.shared.logger_factory import LoggerFactory
import threading
from atproto import Client

log = LoggerFactory.logger(__name__)

apiThreadLock = threading.Lock()


# class BufferedUserTweetGetter():
#     def __init__(self, num_tweets, subscriber, twitter_api, user_ids, q=Queue(), r=Queue()):
#         self.twitter_api = twitter_api
#
#         num_threads = 4
#         self.q = q
#         self.r = r
#
#         self.limit = num_tweets
#         self.subscriber = subscriber
#
#         for user_id in user_ids:
#             self.q.put(user_id)
#
#         api_threads = []
#         worker_threads = []
#
#         # Api threads
#         self.api_threads_running = num_threads
#         for i in range(num_threads):
#             t = Thread(target=self.stream_tweets)
#             t.daemon = True
#             api_threads.append(t)
#             t.start()
#
#         # Worker threads
#         for i in range(num_threads):
#             t = Thread(target=self.do_work)
#             t.daemon = True
#             worker_threads.append(t)
#             t.start()
#
#         self.api_threads = api_threads
#         self.worker_threads = worker_threads
#
#     def stream_tweets(self):
#         while not self.q.empty():
#             try:
#                 user_id = self.q.get(block=True, timeout=5)
#
#                 counter = 0
#                 try:
#                     cursor = Cursor(self.twitter_api.user_timeline, user_id=user_id, count=200,
#                                     since_id='1277627227954458624', exclude_replies=True).items()
#                     for data in cursor:
#                         self.r.put(data)
#                         counter += 1
#                 except TweepError as e:
#                     log.error(e)
#
#                 log.info("Downloaded " + str(counter) + " Tweets for user " + str(user_id))
#             except Exception as ex:
#                 # Exception is empty queue exception
#                 pass
#
#         with apiThreadLock:
#             self.api_threads_running -= 1
#
#     def do_work(self):
#         while self.api_threads_running != 0 or not self.r.empty():
#             try:
#                 data = self.r.get(block=True, timeout=5)
#                 self.subscriber.on_status(data)
#             except Exception as ex:
#                 # Exception is empty queue exception
#                 pass
#

# class BufferedTweepyListener(StreamListener):
#     def __init__(self, num_tweets, subscriber, q=Queue()):
#         super().__init__()
#
#         self.running = True
#
#         num_threads = 4
#         self.q = q
#
#         threads = []
#         for i in range(num_threads):
#             t = Thread(target=self.do_work)
#             t.daemon = True
#             threads.append(t)
#             t.start()
#
#         self.counter = 0
#         self.limit = num_tweets
#
#         self.threads = threads
#
#         self.subscriber = subscriber
#
#     def on_status(self, data):
#         self.q.put(data)
#         self.counter += 1
#
#         if self.counter < self.limit:
#             return True
#         else:
#             self.running = False
#             return False
#
#     def get_data(self):
#         while self.running or not self.q.empty():
#             try:
#                 data = self.q.get(block=True, timeout=5)
#                 if data is not None:
#                     self.subscriber.on_status(data)
#             except Exception as ex:
#                 # Exception is empty exception
#                 pass
#
#     def do_work(self):
#         while self.running or not self.q.empty():
#             try:
#                 data = self.q.get(block=True, timeout=5)
#                 if data is not None:
#                     self.subscriber.on_status(data)
#             except Exception as ex:
#                 # Exception is empty exception
#                 pass


# class TweepyListener(StreamListener):
#     def __init__(self, num_tweets, subscriber):
#         super().__init__()
#
#         self.counter = 0
#         self.limit = num_tweets
#
#         self.subscriber = subscriber
#
#     def on_status(self, data):
#         self.subscriber.on_status(data)
#         self.counter += 1
#
#         return self.counter < self.limit


class BlueSkyAuthenticator():
    client = Client()

    def login(self):
        self.client.on_session_change(self.on_session_change)

        session_string = self.get_session()
        if session_string:
            # print('Reusing session')
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


class TweepyTwitterGetter(TwitterGetter):
    def __init__(self):
        self.client = BlueSkyAuthenticator().login()

    # def stream_tweets_by_user_id_list(self, user_ids, subscriber, num_tweets=0):
    #     getter = BufferedUserTweetGetter(num_tweets=num_tweets, subscriber=subscriber, user_ids=user_ids, twitter_api=self.twitter_api)
    #
    #     api_threads = getter.api_threads
    #     for t in api_threads:
    #         t.join()
    #
    #     log.info("All API threads joined, waiting for worker threads to store tweets")
    #
    #     worker_threads = getter.worker_threads
    #     for t in worker_threads:
    #         t.join()
    #
    #     log.info("Done streaming tweets")

    # def buffered_stream_tweets(self, num_tweets, subscriber) -> None:
    #     # Subscriber is what stores the tweets
    #     listener = BufferedTweepyListener(num_tweets=num_tweets, subscriber=subscriber)
    #
    #     stream = Stream(self.auth, listener)
    #     stream.filter(languages=["en"])
    #     stream.sample()
    #
    #     threads = listener.threads
    #     for t in threads:
    #         t.join()

    # def stream_tweets(self, num_tweets, subscriber) -> None:
    #     """
    #     Creates a twitter stream, which downloads the given number of tweets.
    #     Each time a tweet is downloaded, the subscriber is notified (their
    #     on_status method is called)
    #
    #     @param num_tweets the number of tweets to download
    #     @param subscriber the object to notify each time a tweet is downloaded
    #     """
    #     listener = TweepyListener(num_tweets=num_tweets, subscriber=subscriber)
    #
    #     stream = Stream(self.auth, listener)
    #     stream.filter(languages=["en"])
    #     stream.sample()

    def get_user_by_id(self, user_id: str) -> User:
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
        # cursor = Cursor(self.twitter_api.friends_ids, user_id=user_id, count=5000).items(limit=num_friends)
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

    def get_random_tweet(self):
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
