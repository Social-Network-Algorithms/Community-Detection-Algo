from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_ranker import CommunityRanker
from typing import List
from tqdm import tqdm


class CommunityConsumptionUtilityRanker(CommunityRanker):
    def __init__(self, user_tweets_getter: UserTweetsGetter, friends_getter, ranking_setter):
        self.user_tweets_getter = user_tweets_getter
        self.user_friend_getter = friends_getter
        self.ranking_setter = ranking_setter
        self.ranking_function_name = "indirect consumption utility"

    def score_users(self, user_ids: List[str], respection: List[str]):
        scores = {}
        for user_id in user_ids:
            scores[str(user_id)] = 0

        for user_id in tqdm(user_ids):
            friends = list(
                map(str, self.user_friend_getter.get_user_friends_ids(user_id)))
            retweets = self.user_tweets_getter.get_user_retweets(user_id)

            for retweet in retweets:
                if str(retweet.retweet_user_id) in user_ids and \
                        str(retweet.retweet_user_id) != str(user_id) and \
                        str(retweet.retweet_user_id) in friends:
                    # retweeting your own tweet does not count
                    # only count retweets that are from user's friends
                    scores[str(user_id)] += 1
            # scores[str(id)] *= coefficient
        return scores

    def score_user(self, user_id: str, user_ids: List[str]):
        score = 0

        friends = list(
            map(str, self.user_friend_getter.get_user_friends_ids(id)))
        retweets = self.user_tweets_getter.get_user_retweets(user_id)
        for retweet in retweets:
            if str(retweet.retweet_user_id) in user_ids and \
                    str(retweet.retweet_user_id) != str(user_id) and \
                    str(retweet.retweet_user_id) in friends:
                # retweeting your own tweet does not count
                # only count retweets that are from user's friends
                score += 1
        return score
