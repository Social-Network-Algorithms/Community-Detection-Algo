from dateutil.relativedelta import relativedelta
from typing import List, Dict
from src.model.tweet import Tweet
from src.model.user import User
from src.dao.raw_tweet.getter.raw_tweet_getter import RawTweetGetter
from datetime import datetime


class MongoRawTweetGetter(RawTweetGetter):
    """
    Implementation of TweetGetter that retrieves tweets from MongoDB
    """

    def __init__(self):
        self.collection = None

    def set_tweet_collection(self, collection: str) -> None:
        self.collection = collection

    def get_all_tweets(self):
        return self.collection.find()

    def get_tweet_by_id(self, id: str, user_id: str) -> Tweet:
        """
        Return tweet with id that matches the given id

        @param id the id of the tweet to get
        @param user_id the user id or name associated with the tweet

        @return the Tweet object corresponding to the tweet id, or none if no
            tweet matches the given id
        """
        tweet_doc = self.collection.find_one({"id": str(id), "user_id": str(user_id)})
        if tweet_doc is not None:
            return Tweet.fromDict(tweet_doc)
        else:
            return None

    def get_tweets_by_user(self, user: User) -> List[Tweet]:
        """
        Return a list of tweet with user_id that matches the given user

        @param user the user to retrieve tweets from
        """
        return self.get_tweets_by_user_id(user.id)

    def get_tweets_by_user_id(self, user_id: str) -> List[Tweet]:
        """
        Return a list of tweet with user_id that matches the given user_id

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """

        tweet_doc_list = self.collection.find({"user_id": str(user_id)})

        tweets = []
        for doc in tweet_doc_list:
            tweets.append(Tweet.fromDict(doc))

        return tweets

    def get_tweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        """
        Return a list of tweet with user_id that matches the given user_id
        since a certain time

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """
        from_date = datetime.today() + relativedelta(months=-12)
        # from_date = datetime(2020, 6, 30)
        tweet_doc_list = self.collection.find({"$and": [{"user_id": str(user_id)},
                                                        {"created_at": {"$gte": from_date}}]})
        tweets = []
        for doc in tweet_doc_list:
            tweets.append(Tweet.fromDict(doc))
        return tweets

    def convert_dates(self):
        """
        Converts the string dates into date time objects
        """
        tweet_doc_list = self.collection.find({})
        for tweet in tweet_doc_list:
            date = tweet['created_at']
            if type(date) != datetime:
                proper_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
                pointer = tweet['id']
                self.collection.update({'id': pointer}, {'$set': {'created_at': proper_date}})
                print('updated created_at to datetime\n')
            else:
                print('skipping as is already datetime...\n')

    def convert_dates_for_user_id(self, user_id):
        tweet_doc_list = self.collection.find({"user_id": str(user_id)})
        from tqdm import tqdm
        for tweet in tqdm(tweet_doc_list):
            date = tweet['created_at']
            if type(date) != datetime:
                proper_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
                pointer = tweet['id']
                self.collection.update({'id': pointer}, {'$set': {'created_at': proper_date}})
                # print('updated created_at to datetime\n')
            else:
                # print('skipping as is already datetime...\n')
                pass

    def get_retweets_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:
        """
        Return a list of retweet with user_id that matches the given user_id
        since a certain time

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """
        tweets = self.get_tweets_by_user_id_time_restricted(user_id)

        retweets = []
        for tweet in tweets:
            if tweet.retweet_user_id is not None:  # checks if it is a retweet
                retweets.append(tweet)

        return retweets

    def get_retweets_by_user_id(self, user_id: str) -> List[Tweet]:
        """
        Return a list of retweet with user_id that matches the given user_id

        @param user_id the id of the user to retrieve tweets from

        @return a list of tweets by the given user
        """

        tweets = self.get_tweets_by_user_id(user_id)

        retweets = []
        for tweet in tweets:
            if tweet.retweet_user_id is not None:  # checks if it is a retweet
                retweets.append(tweet)

        return retweets
    
    def get_retweets_ids_by_user_id(self, user_id: str) -> List[str]:
        tweets = self.get_tweets_by_user_id(user_id)

        retweets = []
        for tweet in tweets:
            if tweet.retweet_user_id is not None:
                retweets.append(tweet.retweet_id)
        return retweets

    def contains_tweets_from_user(self, user_id: str):
        # if self.collection.count_documents({"user_id": bson.int64.Int64(user_id)}, limit=1) > 0:
        #     return True
        # return False
        return self.collection.find_one({"user_id": str(user_id)}) is not None

    def get_num_tweets(self) -> int:
        """
        Returns the number of tweets in the mongo collection

        @return the number of tweets
        """
        # We call count with a blank query {} so that it returns an accurate
        # result, rather than relying on the metadata which gives an approximate
        # result. However this is slower
        return self.collection.count({})

    def get_all_retweets_dict(self) -> Dict[str, List[Tweet]]:
        """Return a dictionary of all retweets in the format {key: retweet_user_id, value:[Tweet]}"""
        all_retweets_dict = {}
        for doc in self.collection.find():
            user_id = doc["user_id"]
            if user_id not in all_retweets_dict:
                all_retweets_dict[user_id] = []
            if doc["retweet_user_id"] is not None:
                all_retweets_dict[user_id].append(doc)

        return all_retweets_dict

    def get_retweets_of_user_by_user_id(self, user_id: str) -> List[Tweet]:
        retweet_doc_list = self.collection.find({"retweet_user_id": str(user_id)})

        retweets = []
        for doc in retweet_doc_list:
            retweets.append(Tweet.fromDict(doc))

        return retweets

    def get_retweets_of_user_by_user_id_time_restricted(self, user_id: str) -> List[Tweet]:

        from_date = datetime.today() + relativedelta(months=-12)
        # from_date = datetime(2020, 6, 30)
        retweet_doc_list = self.collection.find({"$and": [{"retweet_user_id": str(user_id)},
                                                        {"created_at": {"$gte": from_date}}]})
        retweets = []
        for doc in retweet_doc_list:
            retweets.append(Tweet.fromDict(doc))

        return retweets

    def get_tweets_by_user_ids(self, user_ids: List[str]) -> List[Tweet]:
        # Get all tweets of all users in the list
        from_date = datetime(2023, 7, 16) + relativedelta(months=-12)

        # tweet_doc_list = self.collection.find({"user_id": {"$in": user_ids}})
        
        tweet_doc_list = self.collection.find({"$and": [
            {"user_id": {"$in": user_ids}},
            {"created_at": {"$gte": from_date}}
            ]})

        return [Tweet.fromDict(doc) for doc in tweet_doc_list]

    def get_tweet_scale_coefficient(self, user_id) -> float:

        def get_tweet_limit_coefficient_by_tweets_brute_force(tweets: List) -> float:
            earliest = tweets[0].created_at
            for tweet in tweets:
                if tweet.created_at < earliest:
                    earliest = tweet.created_at
            date1 = datetime(2021, 6, 30)
            print(f'first: {date1}, second: {earliest}')
            months_difference = (12 * date1.year + date1.month) - (12 * earliest.year + earliest.month)
            print(f'mons_diff = {months_difference}')
            if months_difference == 0:
                return 12.0
            else:
                return abs(12.0 / months_difference)

        tweets = self.get_tweets_by_user_id_time_restricted(user_id)
        coeffcient = 1
        if len(tweets) >= 3200:
            coeffcient = get_tweet_limit_coefficient_by_tweets_brute_force(tweets)
            print(f'catch {user_id} with coefficient = {coeffcient}')
        return coeffcient
