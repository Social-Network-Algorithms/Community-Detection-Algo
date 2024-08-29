from typing import List

from matplotlib import pyplot as plt

from quality_tests.quality_tests import CommunityQualityTests
from src.shared.utils import get_project_root

PATH = str(get_project_root()) + "/data/tests/"

def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i])

class TestCoreDetection(CommunityQualityTests):
    def run_tests(self, community, seeds, seed_clusters):
        self.test_1(community, seeds)
        self.test_2(community, seed_clusters)
        self.test_3(community, seeds)
        self.test_4(community, seed_clusters)

    def test_1(self, community, seeds):
        """
        test 1: Social rank of seed users at the different iteration should increase
        plot the social support score of the users in the final community and highlight the seed users in the plot
        """
        seed_scores = self.community_social_support_ranker.score_users(seeds, community)
        x_vals = list(range(0, len(seeds)))
        y_vals = list(seed_scores.values())

        path = PATH + self.seed + "/" + "core detection correctness test 1"
        plt.figure("core detection correctness test 1")
        plt.bar(x_vals, y_vals)
        addlabels(x_vals, y_vals)
        plt.ylabel('social support score')
        plt.xlabel('seed users')
        plt.title("Final score of seed users in the final community")
        plt.savefig(path)

    def test_2(self, community, seed_clusters: List[List[str]]):
        """
        test 2: Social rank of top 10 users in cluster at the different iterations should increase
        plot the social support score of the users in the final community and highlight the chosen cluster users in the plot
        """
        community_scores = self.community_social_support_ranker.score_users(community, community)
        sorted_community_scores = dict(sorted(community_scores.items(), key=lambda item: item[1], reverse=True))

        path = PATH + self.seed + "/core detection correctness test 2"
        plt.figure("core detection correctness test 2")
        x_vals = list(range(0, len(community)))
        y_vals = list(sorted_community_scores.values())

        for i in range(len(seed_clusters)):
            cluster = seed_clusters[i]
            # get colors of the seed bars
            color_map = []

            for x in x_vals:
                user = community[x]
                if user in cluster:
                    pos = cluster.index(user)
                    alpha = (pos + 1) / len(cluster)
                    color_map.append([1, 0.4, 0.3, alpha])
                else:
                    color_map.append([0.7, 0.7, 0.7, 1])

            plt.subplot(len(seed_clusters), 1, i + 1)
            plt.bar(x_vals, y_vals, color=color_map)
            plt.title('iteration ' + str(i))
            if i == len(seed_clusters) - 1:
                plt.xlabel('users ranked from highest to lowest score')
                plt.ylabel('Final social support score')
        # plt.show()
        plt.savefig(path)

    def test2_helper(self, user, seed_clusters):
        """Return the clusters the users is included in or empty otherwise"""
        included_clusters = []
        for cluster in seed_clusters:
            if user in cluster:
                included_clusters.append(cluster)
        return included_clusters

    def test_3(self, community, seeds):
        """
        Test 3: Are all seed users included in community
        """
        not_included_users = []
        all_included = True
        for seed in seeds:
            if seed not in community:
                all_included = False
                not_included_users.append(self.user_getter.get_user_by_id(seed).screen_name)

        print("Not included seeds in the community: ", not_included_users)
        return all_included # all were included

    def test_4(self, community, seed_clusters):
        """
        Test 4: What fraction of top 10 users in clusters are included in community
        """
        all_users_len, included_users_len = 0, 0

        for cluster in seed_clusters:
            for seed in cluster:
                all_users_len += 1
                if seed in community:
                    included_users_len += 1

        print("fraction of top 10 users in clusters are included in community: ", included_users_len / all_users_len)
        return included_users_len / all_users_len # 90%
