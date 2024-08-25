
class CommunityQualityTests():
    def __init__(self, user_getter, retweeted_users_getter, user_friend_getter, community_social_support_ranker, initial_seed):
        self.community_social_support_ranker = community_social_support_ranker
        self.user_getter = user_getter
        self.retweeted_users_getter = retweeted_users_getter
        self.user_friend_getter = user_friend_getter
        self.seed = initial_seed

    def run_tests(self, community, seeds, seed_clusters):
        return
