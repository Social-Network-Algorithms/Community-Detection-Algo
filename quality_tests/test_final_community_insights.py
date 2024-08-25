from matplotlib import pyplot as plt

from quality_tests.quality_tests import CommunityQualityTests
from src.shared.utils import get_project_root

PATH = str(get_project_root()) + "/data/tests/"

class TestCommunityInsights(CommunityQualityTests):

    def run_tests(self, community, seeds, seed_clusters):
        self.test_1(community)
        self.test_2(community)

    def test_1(self, community):
        """
        Social rank vs number of followers in community
        """
        community_scores = self.community_social_support_ranker.score_users(community, community)
        sorted_community_scores = dict(sorted(community_scores.items(), key=lambda item: item[1], reverse=True))

        x_vals = list(range(0, len(community)))
        y_vals = []
        for u in sorted_community_scores.keys():
            y_vals.append(self._get_local_follower_count(u, community))

        path = PATH + self.seed + "/final community insights test 1"
        plt.figure("final community insights test 1")

        plt.bar(x_vals, y_vals)
        plt.ylabel('local followers')
        plt.xlabel('users ranked from highest to lowest score')
        plt.title('social rank vs the number of local followers')
        plt.savefig(path)

    def test_2(self, community):
        """
        Social rank vs number of following (friends) in community
        """
        community_scores = self.community_social_support_ranker.score_users(community, community)
        sorted_community_scores = dict(sorted(community_scores.items(), key=lambda item: item[1], reverse=True))

        x_vals = list(range(0, len(community)))
        y_vals = []
        for u in sorted_community_scores.keys():
            y_vals.append(self._get_local_following_count(u, community))

        path = PATH + self.seed + "/final community insights test 2"
        plt.figure("final community insights test 2")

        plt.bar(x_vals, y_vals)
        plt.ylabel('local friends')
        plt.xlabel('users ranked from highest to lowest score')
        plt.title('social rank vs the number of local friends')
        plt.savefig(path)

    def _get_local_follower_count(self, user, user_ids):
        count = 0
        for user2 in user_ids:
            friend2 = self.user_friend_getter.get_user_friends_ids(user2)
            if user in friend2:
                count += 1
        return count

    def _get_local_following_count(self, user, user_ids):
        friend1 = self.user_friend_getter.get_user_friends_ids(user)
        count = 0
        for user2 in user_ids:
            if user2 in friend1:
                count += 1
        return count
