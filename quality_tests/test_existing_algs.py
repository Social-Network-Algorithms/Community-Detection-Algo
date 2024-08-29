from matplotlib import pyplot as plt

from quality_tests.quality_tests import CommunityQualityTests
from src.shared.utils import get_project_root

PATH = str(get_project_root()) + "/data/tests/"


# function to add value labels
def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i])


def read_other_community_file():
    community = []
    with open('other_community.txt') as file:
        for line in file:
            user_id = line[:-1]
            community.append(user_id)
    return list(set(community))


class TestExistingAlgs(CommunityQualityTests):
    def run_tests(self, community, seeds, seed_clusters):
        other_community = read_other_community_file()
        self.test_1(other_community, seeds)
        self.test_2(community, other_community)
        self.test_3(community, other_community)

    def test_1(self, other_comm, seeds):
        """
        Test 1: Social rank of our detected seed users in their final community
        """
        self.test_1_helper(seeds, other_comm, "existing algorithms test 1 (other comm)",
                          "Final score of seed users in the final community")

    def test_1_helper(self, comm1, comm2, fig_name, title):
        community_scores = self.community_social_support_ranker.score_users(comm1, comm2)
        x_vals = list(range(0, len(comm1)))
        y_vals = list(community_scores.values())

        path = PATH + self.seed + "/" + fig_name
        plt.figure(fig_name)
        plt.bar(x_vals, y_vals)
        addlabels(x_vals, y_vals)
        plt.ylabel('social support score')
        plt.xlabel('users')
        plt.title(title)
        plt.savefig(path)

    def test_2(self, main_comm, alg_comm):
        """
        Test 2: Social rank of members in our detected community in the other final community
        """
        self.test_2_helper(alg_comm, main_comm, "existing algorithms test 2 (alg comm in main comm)",
                           "Final score of alg users in the main community")
        self.test_2_helper(alg_comm, alg_comm, "existing algorithms test 2 (alg comm in alg comm)",
                           "Final score of alg users in the alg community")

    def test_2_helper(self, main_comm, other_comm, fig_name, title):
        community_scores = self.community_social_support_ranker.score_users(main_comm, other_comm)
        sorted_community_scores = dict(sorted(community_scores.items(), key=lambda item: item[1], reverse=True))
        x_vals = list(range(0, len(main_comm)))
        y_vals = list(sorted_community_scores.values())

        path = PATH + self.seed + "/" + fig_name
        plt.figure(fig_name)
        plt.bar(x_vals, y_vals)
        plt.ylabel('social support score')
        plt.xlabel('seed users')
        plt.title(title)
        plt.savefig(path)

    def test_3(self, main_comm, alg_comm):
        """
        Test 3: Coverage of members in our detected community in the other final community
        """
        self.test_3_helper(alg_comm, main_comm, "existing algorithms test 3 (alg comm in main comm)",
                           "Coverage of alg users in the main community")
        self.test_3_helper(alg_comm, alg_comm, "existing algorithms test 3 (alg comm in alg comm)",
                           "Coverage of alg users in the alg community")

    def test_3_helper(self, comm1, comm2, fig_name, title):
        community_scores = self.community_social_support_ranker.score_users(comm1, comm2)
        sorted_community_scores = dict(sorted(community_scores.items(), key=lambda item: item[1], reverse=True))

        coverage = {}
        for user in sorted_community_scores.keys():
            retweeted_users = list(set(self.retweeted_users_getter.get_retweet_users_ids(user)))
            if user in retweeted_users:
                retweeted_users.remove(user)
            coverage[user] = len(set(retweeted_users).intersection(comm2))

        x_vals = list(range(0, len(comm1)))
        y_vals = list(coverage.values())

        path = PATH + self.seed + "/" + fig_name
        plt.figure(fig_name)
        plt.bar(x_vals, y_vals)
        plt.ylabel('coverage')
        plt.xlabel('users')
        plt.title(title)
        plt.savefig(path)
