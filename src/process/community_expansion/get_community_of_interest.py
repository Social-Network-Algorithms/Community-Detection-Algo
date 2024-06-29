from typing import Tuple, Set
import src.clustering_experiments.build_cluster_tree as bct
from src.process.community_ranking.community_influence_one_ranker import CommunityInfluenceOneRanker
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker


class GetCommunityOfInterest():
    def __init__(self, user_getter, ranker_list, user_tweets_getter, user_friend_getter):
        self.user_getter = user_getter
        self.ranker_list = ranker_list

        self.community_social_support_ranker = CommunitySocialSupportRanker(user_tweets_getter, user_friend_getter,
                                                                            None)
        self.community_influence1_ranker = CommunityInfluenceOneRanker(user_tweets_getter, user_friend_getter,
                                                                            None)

    def get_communities_of_user(self, user_id):
        """
        Perform weighted walktrap clustering algorithm on the core ot the candidate user to get the clusters(communities)
        that the user belongs to.
        """
        screen_name = self.user_getter.get_user_by_id(user_id).screen_name
        user_activity = "user retweets"
        refined_clusters = bct.clustering_from_social_graph(screen_name, user_activity=user_activity, iter=1)
        sorted_clusters = sorted(refined_clusters, key=lambda c: len(c.users), reverse=True)
        return sorted_clusters

    def get_main_community_user(self, user_id) -> Tuple[Set[str], float]:
        """
        Among the communities the core or the candidate user belongs to, pick the one with the highest social support score
        and return the desired community and its score
        """
        clusters = self.get_communities_of_user(user_id)
        cluster_scores = {cluster: 0.0 for cluster in clusters}
        for cluster in clusters:
            # social support
            respection = cluster.users
            # influence1_ranker_score = self.community_influence1_ranker.score_user(user_id, respection)
            social_support_ranker_score = self.community_social_support_ranker.score_user(user_id, respection)
            cluster_scores[cluster] = social_support_ranker_score

        if len(cluster_scores) != 0:
            chosen_cluster = max(cluster_scores, key=cluster_scores.get)
            return set(chosen_cluster.users), cluster_scores[chosen_cluster]
        else:
            return set(), 0

    def get_main_community(self, core_user_ids, ranker_threshold) -> Tuple[Set[str], float]:
        """
        Get the main community of interest by unioning the main community that each core user belongs to.
        """
        main_community = set()
        main_community_score = 0
        for core_user in core_user_ids:
            chosen_community, chosen_community_score = self.get_main_community_user(core_user)
            main_community = main_community.union(chosen_community)
            main_community_score += chosen_community_score

        return main_community, main_community_score * ranker_threshold
