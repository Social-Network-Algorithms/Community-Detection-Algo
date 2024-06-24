from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List


class CommunityRelativeProductionRanker(CommunityRanker):
    def __init__(self, cluster_getter, user_tweets_getter: UserTweetsGetter, ranking_setter, user_getter):
        self.cluster_getter = cluster_getter
        self.user_tweets_getter = user_tweets_getter
        self.ranking_setter = ranking_setter
        self.user_getter = user_getter
        self.ranking_function_name = "relative production"

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {}
        for id in user_ids:
            scores[str(id)] = 0

        for id in user_ids:
            retweets = self.user_tweets_getter.get_retweets_by_user_id_time_restricted(id)
            user = self.user_getter.get_user_by_id(id)
            for retweet in retweets:
                # print(str(str(retweet.user_id) in user_ids) + " " + str(str(retweet.user_id) == id))
                if str(retweet.user_id) in user_ids and str(retweet.user_id) != str(id):
                    scores[str(id)] += 1
            scores[str(id)] /= user.statuses_count

        return scores
