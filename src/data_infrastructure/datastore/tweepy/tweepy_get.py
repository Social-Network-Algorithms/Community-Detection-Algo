import datetime

from atproto_client import SessionEvent, Session

import conf.credentials as credentials

from typing import Union, Optional
from tweepy.streaming import StreamListener
from atproto import Client

class TweepyListener(StreamListener):
    def __init__(self, num_tweets):
        super().__init__()
        self.counter = 0
        self.limit = num_tweets
        self.tweets = []

    def on_status(self, data):
        try:
            self.tweets.append(data)
            self.counter += 1
            if self.counter < self.limit:
                return True
            else:
                return False
        except BaseException as e:
            print('failed on_status,',str(e))


class TweepyGetDAO():
    client = Client()
    def __init__(self):
        self.client.on_session_change(self.on_session_change)

        session_string = self.get_session()
        if session_string:
            # print('Reusing session')
            self.client.login(session_string=session_string)
        else:
            # print('Creating new session')
            self.client.login(credentials.USER_NAME, credentials.PASSWORD)

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



    

    

