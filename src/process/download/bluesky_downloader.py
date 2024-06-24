from typing import Union, List

from src.dao.bluesky.bluesky_dao import BlueSkyGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.model.tweet import Tweet

class BlueskyTweetDownloader():
    """
    Download Tweets for use in future algorithms.
    """
    def gen_user_tweets(self, id: Union[str, int], bluesky_getter: BlueSkyGetter, user_tweets_setter: UserTweetsSetter, num_tweets=None, start_date=None, end_date=None) -> List[Tweet]:
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

    # def gen_user_tweets_in_timeframe(self, id: Union[str, int], start_date: datetime,
    #                                  end_date: datetime, get_dao, set_dao, num_tweets=None):
    #     """
    #     Return num_tweets tweets/retweets made by user with id(username or user id) id between start_date and end_date.
    #     """

    #     tweets, retweets = get_dao.get_tweets_by_timeframe_user(id, start_date, end_date, num_tweets)
    #     set_dao.store_tweet_by_user(id, tweets, retweets)

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

class BlueskyFriendsDownloader():
    """
    Download Bluesky Friends for use in future algorithms.
    """
    def gen_friends_by_screen_name(self, screen_name: str, bluesky_getter: BlueSkyGetter, user_friends_setter, num_friends=None) -> List[str]:
        """
        Retrieves a list of screen_names of friends for the user with the given screen name

        @param screen_name the screen name of the user to query on
        @param bluesky_getter the getter to access bluesky with
        @param user_friends_setter the dao to store the output
        @param num_friends Optional - if specified, the maximum number of friends to retrieve

        @return a list of screen names of users
        """

        assert type(screen_name) == str

        user_id, friends = bluesky_getter.get_friends_ids_by_screen_name(screen_name, num_friends)
        user_friends_setter.store_friends(user_id, friends)

        return friends

    def gen_friends_ids_by_screen_name_or_id(self, screen_name: str, bluesky_getter: BlueSkyGetter, user_friends_setter, num_friends=None) -> List[str]:
        """
        Retrieves a list of friend_ids of friends for the user with the given screen name or id

        @param screen_name the screen name or id of the user to query on
        @param bluesky_getter the getter to access bluesky with
        @param user_friends_setter the dao to store the output
        @param num_friends Optional - if specified, the maximum number of friends to retrieve

        @return a list of ids of friends
        """
        assert type(screen_name) == str

        user_id, friends_ids = bluesky_getter.get_friends_ids_by_screen_name(screen_name, num_friends)
        user_friends_setter.store_friends(user_id, friends_ids)
        return friends_ids

    def gen_friends_by_id(self, id: str, bluesky_getter: BlueSkyGetter, user_friends_setter, num_friends=None) -> List[str]:
        """
        Retrieves a list of ids of friends for the user with the given id

        @param id the id of the user to query on
        @param bluesky_getter the getter to access bluesky with
        @param user_friends_setter the dao to store the output in
        @param num_friends Optional - if specified, the maximum number of friends to retreive

        @return a list of ids of users friends with the given user
        """

        assert type(id) == str

        _, friends_ids = bluesky_getter.get_friends_ids_by_user_id(id, num_friends)
        user_friends_setter.store_friends(id, friends_ids)
        return friends_ids

    def gen_user_local_neighborhood(self, user: str, bluesky_getter: BlueSkyGetter, user_friends_getter, user_friends_setter):
        """
        Gets and stores friends, as well as friends of friends for a given user

        @param user the screen name of the user to build the network for
        @param bluesky_getter the dao to access bluesky with
        @param user_friends_getter the dao to access the given users friends with
        @param user_friends_setter the dao to store the local network in
        """
        # get the user id from user's screen_name
        user_id = bluesky_getter.get_user_by_id(user).id
        user_friends_ids_list = user_friends_getter.get_user_friends_ids(user_id)
        if not user_friends_ids_list:
            user_friends_ids_list = self.gen_friends_by_id(user_id, bluesky_getter, user_friends_setter, None)

        for friend_id in user_friends_ids_list:
            friend_friends_ids_list = user_friends_getter.get_user_friends_ids(friend_id)
            if not friend_friends_ids_list:
                self.gen_friends_by_id(friend_id, bluesky_getter, user_friends_setter, None)


class BlueskyFollowersDownloader():
    """
    Download Bluesky Followers for use in future algorithms.
    """

    def gen_followers_by_screen_name_or_id(self, screen_name: str, bluesky_getter: BlueSkyGetter, user_followers_setter, num_followers=None) -> List[str]:
        """
        Gets a list of followers of a user by screen name

        @param screen_name the screen name or id of the user to search for
        @param bluesky_getter the dao to access bluesky with
        @param user_followers_setter the dao to store the users followers in
        @param num_followers the maximum number of followers to retrieve

        @return a list of ids of followers for the given user
        """
        assert type(screen_name) == str

        user_id, followers_users_ids = bluesky_getter.get_followers_ids_by_screen_name(screen_name, num_followers)
        user_followers_setter.store_followers(user_id, followers_users_ids)


# def rate_limited_functions() -> str:
#     functions_list = ["get_user_tweets_by_screen_name", "get_user_tweets_by_id",
#                       "get_friends_screen_names_by_screen_name", "get_friends_ids_by_id"]

#     result = ""
#     for function_name in functions_list:
#         result += function_name + "\n"
#     return result.strip()


# def filter_out_bots(users: List[str], start: datetime, end: datetime, threshold=0.75) -> List[str]:
#     """
#     Filters out bots from the supplied list of screen names. An account is flagged as a bot
#     if more than the given threshold of total tweets supplied by the account in the given
#     timeframe are retweets.
#     """
#     li = []
#     for user in users:
#         retweets, tweets = self.get_tweets(user, start, end)
#         if len(retweets) + len(tweets) > 0 and (len(retweets)/(len(tweets)+len(retweets)) <= 0.75):
#             li.append(user)

#     return li
