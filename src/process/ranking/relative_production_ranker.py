from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.model.ranking import Ranking
from src.process.ranking.ranker import Ranker
from typing import List


class RelativeProductionRanker(Ranker):
    def __init__(self, bluesky_getter, cluster_getter, user_tweets_getter: UserTweetsGetter, ranking_setter, user_getter):
        self.bluesky_getter = bluesky_getter
        self.cluster_getter = cluster_getter
        self.user_tweets_getter = user_tweets_getter
        self.ranking_setter = ranking_setter
        self.user_getter = user_getter
        self.ranking_function_name = "relative production"

    def score_users(self, user_ids: List[str]):
        scores = {}
        for id in user_ids:
            scores[str(id)] = 0

        for id in user_ids:
            user = self.user_getter.get_user_by_id(id)
            retweets = self.user_tweets_getter.get_user_retweets(id)
            for retweet in retweets:
                # print(str(str(retweet.user_id) in user_ids) + " " + str(str(retweet.user_id) == id))
                if str(retweet.user_id) in user_ids and str(retweet.user_id) != str(id):
                    scores[str(id)] += 1
            scores[str(id)] /= user.statuses_count

        return scores
