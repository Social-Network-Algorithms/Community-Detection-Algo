from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import Dict, List
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

class CommunityInfluenceTwoRanker(CommunityRanker):
    def __init__(self, user_tweets_getter: UserTweetsGetter, friends_getter, ranking_setter):
        self.user_tweets_getter = user_tweets_getter
        self.friends_getter = friends_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "influence two"

    def create_friends_dict(self, user_ids):
        friends = {}
        for user_id in user_ids:
            friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)
            if friends_of_user_id is None:
                friends[user_id] = []
            else:
                friends[user_id] = [str(id) for id in friends_of_user_id]
        return friends

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {}

        for user_id in user_ids:
            scores[user_id] = self.score_user(user_id, respection)

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

    def _group_by_retweeter(self, tweets) -> Dict:
        # Puts all tweets with the same retweeter in the same list
        # Returns: A dictionary where the key is the user_id of the retweeter and
        # the value is the list of tweets retweeted by the retweeter
        dict = {}
        for tweet in tweets:
            if tweet.retweet_id is None: # tweet is not a retweet
                continue
            key = str(tweet.user_id)
            if key in dict:
                dict[key].append(tweet)
            else:
                dict[key] = [tweet]

        return dict

    def score_user(self, user_id, user_ids: List[str]):
        if user_id not in user_ids:
            user_ids = user_ids + [user_id]
            weight = 1
        else:
            weight = len(user_ids) / (len(user_ids) - 1)

        # Score users by summing up the percentage of tweets they make up in all followers' retweets
        score = 0

        tweets = self.user_tweets_getter.get_tweets_by_user_ids(user_ids)
        # log.info("Get tweets from Database")
        valid_tweets = [tweet for tweet in tweets if tweet.retweet_user_id != tweet.user_id]

        # Define helper functions
        tweets_by_retweet_group = self._group_by_retweet_id(valid_tweets)
        def get_retweets_of_tweet_id(tweet_id):
            return tweets_by_retweet_group.get(str(tweet_id), [])
        def get_later_retweets_of_tweet_id(tweet_id, created_at):
            return [tweet for tweet in get_retweets_of_tweet_id(tweet_id) if tweet.created_at > created_at]

        retweets_by_retweeter = self._group_by_retweeter(valid_tweets)
        def get_num_retweets_by(id):
            return len(retweets_by_retweeter.get(id, []))

        friends = self.create_friends_dict(user_ids)
        def is_direct_follower(a, b): # 'b' is a follower of 'a'
            return a in friends.get(b, [])

        user_tweets = [tweet for tweet in valid_tweets if str(tweet.user_id) == user_id]
        user_original_tweets = [tweet for tweet in user_tweets if tweet.retweet_id is None]
        user_retweets = [tweet for tweet in user_tweets if tweet.retweet_id is not None]

        for follower_id in [other_id for other_id in user_ids if user_id != other_id and is_direct_follower(user_id, other_id)]:
            follower_score = 0
            # Score original tweets
            for original_tweet in user_original_tweets:
                retweets = get_retweets_of_tweet_id(original_tweet.id)
                follower_score += 1 if any(str(rtw.user_id) == follower_id for rtw in retweets) else 0
            # Score retweets
            for user_retweet in user_retweets:
                retweets = get_later_retweets_of_tweet_id(user_retweet.retweet_id, user_retweet.created_at)
                follower_score += 1 if any(str(rtw.user_id) == follower_id for rtw in retweets) else 0

            if get_num_retweets_by(follower_id) > 0:
                follower_score /= get_num_retweets_by(follower_id)
            score += follower_score

        # log.info("Finish scoring influence 2")

        return score
