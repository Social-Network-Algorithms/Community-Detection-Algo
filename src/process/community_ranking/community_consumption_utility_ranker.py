from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List


class CommunityConsumptionUtilityRanker(CommunityRanker):
    def __init__(self, user_tweets_getter: UserTweetsGetter, friends_getter, ranking_setter):
        self.user_tweets_getter = user_tweets_getter
        self.friends_getter = friends_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "consumption utility"

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {}

        for user_id in user_ids:
            scores[user_id] = self.score_user(user_id, respection)

        return scores

    def score_user(self, user_id: str, user_ids: List[str]):
        if user_id not in user_ids:
            user_ids = user_ids + [user_id]

        score = 0

        retweets = self.user_tweets_getter.get_user_retweets(user_id)

        for retweet in retweets:
            if str(retweet.retweet_user_id) in user_ids and \
                    str(retweet.retweet_user_id) != str(user_id):
                # retweeting your own tweet does not count
                score += 1

        return score / len(user_ids)
