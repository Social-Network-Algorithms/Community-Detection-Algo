from typing import Union

from src.dao.bluesky.bluesky_dao import BlueSkyGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.model.tweet import Tweet

class BlueskyTweetDownloader():
    """
    Download Tweets for use in future algorithms.
    """
    def gen_user_tweets(self, id: Union[str, int], bluesky_getter: BlueSkyGetter, user_tweets_setter: UserTweetsSetter, num_tweets=None, start_date=None, end_date=None):
        """
        Retrieves tweets from bluesky from a given user, and stores them

        @param id the id or username of the user
        @param bluesky_getter the dao to retrieve tweets from tweepy
        @param user_tweets_setter the dao to store user tweets with
        @param num_tweets the number of tweets to retrieve
        @param start_date - Optional, the earliest date to pull tweets from
        @param end_date - Optional, the end date to pull tweets from

        @return a list of Tweets
        """
        user_id = bluesky_getter.get_user_by_screen_name(id).id
        if start_date and end_date:
            all_tweets = bluesky_getter.get_tweets_by_user_id(user_id, num_tweets, start_date, end_date)
        elif start_date or end_date:
            raise Exception("Please provide valid start and end dates")
        else:
            all_tweets = bluesky_getter.get_tweets_by_user_id(user_id, num_tweets)
        user_tweets_setter.store_tweets(user_id, all_tweets)

    def gen_random_tweet(self, bluesky_getter: BlueSkyGetter, tweet_setter: UserTweetsSetter) -> Tweet:
        """
        Retrieves a random tweet from Bluesky

        @param bluesky_getter the dao to retrieve tweets from tweepy
        @param tweet_setter the dao to store the raw tweet in

        @return the random tweet
        """
        tweet = bluesky_getter.get_random_tweet()
        tweet_setter.add_user_tweets(tweet.user_id, [tweet])

        return tweet
