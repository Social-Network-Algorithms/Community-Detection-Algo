from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List
from tqdm import tqdm


class CommunityProductionUtilityRanker(CommunityRanker):
    def __init__(self, user_tweets_getter: UserTweetsGetter, friends_getter, ranking_setter):
        self.user_tweets_getter = user_tweets_getter
        self.user_friend_getter = friends_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "retweets"

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {}
        for user_id in user_ids:
            scores[str(user_id)] = 0

        for user_id in tqdm(user_ids):
            retweets = self.user_tweets_getter.get_user_retweets(
                user_id)

            for retweet in retweets:
                # retweet.user_id is the user that retweeted the tweet
                # retweet.retweet_user_id is the tweet owner
                retweet_user_id = str(retweet.user_id)
                retweet_user_friends = list(
                    map(str, self.user_friend_getter.get_user_friends_ids(
                        retweet_user_id)))
                if retweet_user_id in user_ids and \
                        retweet_user_id != str(user_id) and \
                        user_id not in retweet_user_friends:
                    # only count retweets that are not from user's followers
                    scores[str(user_id)] += 1

        return scores

    def score_user(self, user_id, user_ids: List[str]):
        score = 0

        retweets = self.user_tweets_getter.get_user_retweets(
            user_id)

        for retweet in retweets:
            # retweet.user_id is the user that retweeted the tweet
            # retweet.retweet_user_id is the tweet owner
            retweet_user_id = str(retweet.user_id)
            retweet_user_friends = list(
                map(str, self.user_friend_getter.get_user_friends_ids(
                    retweet_user_id)))
            if retweet_user_id in user_ids and \
                    retweet_user_id != str(user_id) and \
                    user_id not in retweet_user_friends:
                # only count retweets that are not from user's followers
                score += 1

        return score