from datetime import datetime
from typing import List, Dict

from dateutil.relativedelta import relativedelta

from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.model.tweet import Tweet


class MongoUserTweetsGetter(UserTweetsGetter):
    def __init__(self):
        self.user_tweets_collection = None

    def get_all_tweets(self) -> List[Tweet]:
        all_tweets = []
        docs = self.user_tweets_collection.find()
        for doc in docs:
            all_tweets += list(map(lambda tweet: Tweet.fromDict(tweet), doc["tweets"]))
        return all_tweets

    def get_all_tweets_dict(self) -> Dict[str, List[Tweet]]:
        all_tweets_dict = {}
        docs = self.user_tweets_collection.find()
        for doc in docs:
            all_tweets_dict[doc["user_id"]] = list(map(lambda tweet: Tweet.fromDict(tweet), doc["tweets"]))
        return all_tweets_dict

    def get_all_retweets_dict(self) -> Dict[str, List[Tweet]]:
        """Return a dictionary of all retweets in the format {key: retweet_user_id, value:[Tweet]}"""
        all_retweets_dict = {}
        docs = self.user_tweets_collection.find()
        for doc in docs:
            for tweet in doc["tweets"]:
                retweet_user_id = tweet["retweet_user_id"]
                if retweet_user_id is not None:
                    if retweet_user_id not in all_retweets_dict:
                        all_retweets_dict[retweet_user_id] = []
                    all_retweets_dict[retweet_user_id] += Tweet.fromDict(tweet)

        return all_retweets_dict

    def set_user_tweets_collection(self, user_tweets_collection: str) -> None:
        self.user_tweets_collection = user_tweets_collection

    def get_user_tweets(self, user_id: str) -> List[Tweet]:
        """Given a user id, return the tweets"""
        doc = self.user_tweets_collection.find_one({"user_id":str(user_id)})
        if doc is not None:
            return list(map(lambda tweet: Tweet.fromDict(tweet), doc["tweets"]))
        else:
            return None

    def get_tweets_by_user_ids(self, user_ids: List[str]) -> List[Tweet]:
        """Given a user id, return the tweets"""
        all_tweets = []
        for user_id in user_ids:
            doc = self.user_tweets_collection.find_one({"user_id":str(user_id)})
            if doc is not None:
                all_tweets += list(map(lambda tweet: Tweet.fromDict(tweet), doc["tweets"]))
        return all_tweets

    def get_tweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        from_date = datetime.today() + relativedelta(months=-12)
        # from_date = datetime(2020, 6, 30)
        doc = self.user_tweets_collection.find_one({"user_id":str(user_id)})
        tweets = []
        if doc is not None:
            for tweet in doc["tweets"]:
                if tweet["created_at"] >= from_date:
                    tweets += Tweet.fromDict(tweet)
            return tweets
        else:
            return None

    def get_user_retweets(self, user_id: str) -> List[Tweet]:
        """Given a user id, return the tweets"""
        doc = self.user_tweets_collection.find_one({"user_id": str(user_id)})
        retweets = []
        if doc is not None:
            for tweet in doc["tweets"]:
                if tweet["retweet_user_id"] is not None:
                    retweets.append(Tweet.fromDict(tweet))
        return retweets

    def get_retweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        tweets = self.get_tweets_by_user_id_time_restricted(user_id)
        retweets = []
        for tweet in tweets:
            if tweet.retweet_user_id is not None:  # checks if it is a retweet
                retweets.append(tweet)

        return retweets

    def get_retweets_ids_by_user_id(self, user_id: str) -> List[str]:
        tweets = self.get_user_tweets(user_id)

        retweets = []
        for tweet in tweets:
            if tweet.retweet_user_id is not None:
                retweets.append(tweet.retweet_id)
        return retweets

    def convert_dates(self):
        """
        Converts the string dates into date time objects
        """
        docs = self.user_tweets_collection.find({})
        for doc in docs:
            user_id = doc["user_id"]
            updated_tweets = []
            for tweet in doc["tweets"]:
                date = tweet['created_at']
                if type(date) != datetime:
                    proper_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
                    tweet['created_at'] = proper_date
                    print('updated created_at to datetime\n')
                else:
                    print('skipping as is already datetime...\n')
                updated_tweets += tweet

            updated_doc = {"user_id": str(user_id), "tweets": updated_tweets}
            self.user_tweets_collection.find_one_and_replace({"user_id": str(doc["user_id"])}, updated_doc)

    def contains_user(self, user_id: str) -> bool:
        return self.user_tweets_collection.find_one({"user_id": str(user_id)}) is not None
