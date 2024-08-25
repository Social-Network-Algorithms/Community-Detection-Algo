from matplotlib import pyplot as plt

from quality_tests.quality_tests import CommunityQualityTests
from src.shared.utils import get_project_root

PATH = str(get_project_root()) + "/data/tests/"

class TestCoreExpansion(CommunityQualityTests):

    def run_tests(self, community, seeds, seed_clusters):
        self.test_1(community)
        self.test_2(community)

    def test_1(self, community):
        """
        Social score of users in community (should be high)
        """
        community_scores = self.community_social_support_ranker.score_users(community, community)
        sorted_community_scores = dict(sorted(community_scores.items(), key=lambda item: item[1], reverse=True))

        x_vals = list(range(0, len(community)))
        y_vals = list(sorted_community_scores.values())
        path = PATH + self.seed + "/core expansion correctness test 1"
        plt.figure("core expansion correctness test 1")

        plt.bar(x_vals, y_vals)
        plt.ylabel('Final social support score')
        plt.xlabel('users ranked from highest to lowest score')
        plt.title('Final score of users in the final community')
        plt.savefig(path)

    def test_2(self, community):
        """
        Coverage of users in community (should be high)
        coverage: the fraction of the community for which a given community member retweets content.
        """
        community_scores = self.community_social_support_ranker.score_users(community, community)
        sorted_community_scores = dict(sorted(community_scores.items(), key=lambda item: item[1], reverse=True))

        coverage = {}
        for user in list(sorted_community_scores.keys()):
            retweeted_users = list(set(self.retweeted_users_getter.get_retweet_users_ids(user)))
            if user in retweeted_users:
                retweeted_users.remove(user)
            coverage[user] = len(set(retweeted_users).intersection(community))

        x_vals = list(range(0, len(community)))
        y_vals = list(coverage.values())
        path = PATH + self.seed + "/core expansion correctness test 2"
        plt.figure("core expansion correctness test 2")

        plt.bar(x_vals, y_vals)
        plt.ylabel('Coverage')
        plt.xlabel('users ranked from highest to lowest score')
        plt.title('coverage score of users in the final community')
        plt.savefig(path)
