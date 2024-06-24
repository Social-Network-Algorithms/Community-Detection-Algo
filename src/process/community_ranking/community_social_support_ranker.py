from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import Dict, List
from tqdm import tqdm

class CommunitySocialSupportRanker(CommunityRanker):
    def __init__(self, user_tweets_getter: UserTweetsGetter, friends_getter, ranking_setter, alpha=1.0):
        self.friends_getter = friends_getter
        self.user_tweets_getter = user_tweets_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "retweets"
        self.alpha = alpha

    def create_friends_dict(self, user_ids):
        friends = {}
        for user_id in user_ids:
            friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)
            # print("the friends of " + user_id + " are " + str(friends_of_user_id))
            if friends_of_user_id is None:
                friends[user_id] = []
            else:
                friends[user_id] = [str(id) for id in friends_of_user_id]
        return friends

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {user_id: 0 for user_id in user_ids} # Initialize all scores to 0
        friends = self.create_friends_dict(user_ids)
        tweets = self.user_tweets_getter.get_tweets_by_user_ids(user_ids)
        # Omit self-retweets
        tweets = [tweet for tweet in tweets if tweet.user_id != tweet.retweet_id]
        tweets_by_retweet_group = self._group_by_retweet_id(tweets)
        def get_retweets_of_tweet_id(tweet_id):
            return tweets_by_retweet_group.get(str(tweet_id), [])
        def get_later_retweets_of_tweet_id(tweet_id, created_at):
            return [tweet for tweet in get_retweets_of_tweet_id(tweet_id) if tweet.created_at > created_at]
        def is_direct_follower(a, b):
            # b follows a
            return a in friends.get(b, [])

        for id in tqdm(user_ids):
            user_tweets = [tweet for tweet in tweets if str(tweet.user_id) == id]
            original_tweet_ids = [tweet.id for tweet in user_tweets if tweet.retweet_id is None]
            for original_tweet_id in original_tweet_ids:
                retweets = get_retweets_of_tweet_id(original_tweet_id)
                scores[id] += len(retweets)

            user_retweets = [tweet for tweet in user_tweets if tweet.retweet_id is not None]
            for user_retweet in user_retweets:
                retweets = get_later_retweets_of_tweet_id(user_retweet.retweet_id, user_retweet.created_at)
                # The person who retweeted is a direct follower of id.
                retweets_from_direct_followers = [rtw for rtw in retweets if is_direct_follower(id, str(rtw.user_id))]
                scores[id] += len(retweets_from_direct_followers) * self.alpha

        return scores

    def _group_by_retweet_id(self, tweets) -> Dict:
        # Puts all tweets with the same retweet_id in the same list
        # Returns: A dictionary where the key is the retweet_id and
        # the value is the list of tweets with that retweet_id
        dict = {}
        for tweet in tweets:
            key = str(tweet.retweet_id)
            if key in dict:
                dict[key].append(tweet)
            else:
                dict[key] = [tweet]

        return dict
