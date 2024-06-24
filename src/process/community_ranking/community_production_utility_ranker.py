from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List, Dict


class CommunityProductionUtilityRanker(CommunityRanker):
    def __init__(self, user_tweets_getter: UserTweetsGetter, friends_getter, ranking_setter):
        self.user_tweets_getter = user_tweets_getter
        self.user_friend_getter = friends_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "production utility"
        self.all_respection_tweets = []
        self.tweets_by_retweet_group = {}

    def score_users(self, user_ids: List[str], respection: List[str]):
        for user in respection:
            user_tweets = self.user_tweets_getter.get_user_tweets(user)
            self.all_respection_tweets += user_tweets

        self.tweets_by_retweet_group = self._group_by_retweet_id(self.all_respection_tweets)

        scores = {}
        for user_id in user_ids:
            scores[user_id] = self.score_user(user_id, respection)

        return scores

    def score_user(self, user_id, user_ids: List[str]):
        if user_id not in user_ids:
            user_ids = user_ids + [user_id]

        score = 0
        original_tweet_ids = [tweet.id for tweet in self.user_tweets_getter.get_user_tweets(user_id) if tweet.retweet_id is None]
        for original_tweet_id in original_tweet_ids:
            retweets = self.tweets_by_retweet_group.get(str(original_tweet_id), [])
            valid_retweets = [retweet for retweet in retweets if
                              retweet.retweet_user_id != retweet.user_id]  # omit self-retweets
            score += len(valid_retweets)

        return score / len(user_ids)

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