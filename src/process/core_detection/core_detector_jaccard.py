from src.dao.retweeted_users.getter.retweet_users_getter import RetweetUsersGetter
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker
from src.shared.logger_factory import LoggerFactory
import src.clustering_experiments.build_cluster_tree as bct

log = LoggerFactory.logger(__name__)


class JaccardCoreDetector():
    """
    Given an initial user, and a "community/topic", determine the core user of
    that community
    """

    def __init__(self, user_getter, user_downloader, user_tweets_getter,
                 user_friend_getter, retweeted_users_getter: RetweetUsersGetter, sosu_ranker):
        self.user_getter = user_getter
        self.user_downloader = user_downloader
        self.user_friend_getter = user_friend_getter
        self.user_tweets_getter = user_tweets_getter
        self.retweeted_users_getter = retweeted_users_getter
        self.sosu_ranker = sosu_ranker
        self.community_social_support_ranker = CommunitySocialSupportRanker(self.user_tweets_getter,
                                                                            self.user_friend_getter,
                                                                            None)

    def detect_core_by_screen_name(self, screen_name: str, user_activity: str):
        user = self.user_getter.get_user_by_screen_name(screen_name)
        if user is None:
            log.info("Downloading initial user " + str(screen_name))

            self.user_downloader.download_user_by_screen_name(screen_name)
            user = self.user_getter.get_user_by_screen_name(screen_name)

            if user is None:
                msg = "Could not download initial user " + str(screen_name)
                log.error(msg)
                raise Exception(msg)

        log.info("Beginning Core detection algorithm with initial user " + str(screen_name))
        return self.detect_core(user.id, user_activity)

    def detect_core(self, initial_user_id: str, user_activity: str):
        log.info("Beginning core detection algorithm for user with id " + str(initial_user_id))

        seeds = [str(initial_user_id)]
        curr_user_id = None
        top_10_users = []
        seed_clusters = []
        clusters = []
        # First iteration
        i = 0
        try:
            i += 1
            curr_user_id, top_10_users, cluster = self.first_iteration(seeds[0], user_activity)
            seed_clusters.append(top_10_users)
            clusters.append(cluster)
        except Exception as e:
            log.exception(e)
            exit()

        # Next iterations
        while str(curr_user_id) not in seeds:
            log.info("Curr user id: " + str(curr_user_id))
            log.info(f"Prev users list: {seeds}")
            seeds.append(str(curr_user_id))

            try:
                i += 1
                curr_user_id, top_10_users, cluster = self.loop_iteration(curr_user_id, user_activity, top_10_users)
                seed_clusters.append(top_10_users)
                clusters.append(cluster)
            except Exception as e:
                log.exception(e)
                exit()

        # log.info("The previous user id list is " + str(prev_user_id))
        # log.info("The final user for initial user " + str(initial_user_id) + " is "
        #          + self.user_getter.get_user_by_id(str(curr_user_id)).screen_name)
        # This is the core
        log.info(f"The top 10 users for the selected cluster in the last iteration were: {top_10_users}")
        # log.info(f"The top 10 users for the selected cluster in each iteration were:")
        # for top in top_10:
        #     log.info(top)
        # log.info(f"The selected cluster in each iteration were:")

        return top_10_users, seeds, seed_clusters

    def first_iteration(self, user_id: str, user_activity: str):
        clusters = self._clustering(user_id, user_activity, leaves=True)
        chosen_cluster = self.select_first_cluster(user_id, clusters)
        print(chosen_cluster.users)
        print(chosen_cluster.top_users)

        sosu_ranker_scores = self.sosu_ranker.score_users(chosen_cluster.users)
        sosu_ranking = list(
            sorted(sosu_ranker_scores, key=lambda x: (sosu_ranker_scores[x][0], sosu_ranker_scores[x][1]),
                   reverse=True))
        top_10_users = sosu_ranking[:10]

        log.info("top_10 of chosen cluster:")
        log.info(top_10_users)
        curr_user = top_10_users[0]

        return curr_user, top_10_users, chosen_cluster

    def select_first_cluster(self, seed_user, leaf_clusters):
        """Returns the leaf cluster for which the initial seed user receives the highest social support from."""
        cluster_scores = {cluster: 0.0 for cluster in leaf_clusters}

        for cluster in leaf_clusters:
            # social support
            sosu_ranker_scores = self.sosu_ranker.score_users(cluster.users)
            sosu_ranking = list(
                sorted(sosu_ranker_scores, key=lambda x: (sosu_ranker_scores[x][0], sosu_ranker_scores[x][1]),
                       reverse=True))

            current_top_10_users = sosu_ranking[:10]
            cluster_scores[cluster] = self.community_social_support_ranker.score_user(seed_user, current_top_10_users)

        return max(cluster_scores, key=cluster_scores.get)

    def loop_iteration(self, user_id: str, user_activity, curr_top_10_users):
        clusters = self._clustering(user_id, user_activity)
        # clusters only keeps the largest intact ones, as in the report
        # now it selects by social support utility
        chosen_cluster = self._select_cluster(curr_top_10_users, clusters)
        log.info("The algorithm chooses cluster...")
        if chosen_cluster.id is None:
            log.info("Cluster index: " + str(clusters.index(chosen_cluster)))
        else:
            log.info("Cluster id: " + str(chosen_cluster.id))

        sosu_ranker_scores = self.sosu_ranker.score_users(chosen_cluster.users)
        sosu_ranking = list(
            sorted(sosu_ranker_scores, key=lambda x: (sosu_ranker_scores[x][0], sosu_ranker_scores[x][1]),
                   reverse=True))
        top_10_users = sosu_ranking[:10]
        curr_user = top_10_users[0]

        return curr_user, top_10_users, chosen_cluster

    def _select_cluster(self, previous_top_10_users, clusters):
        """Returns the cluster which the previous top 10 users receive the highest social support from.."""
        log.info("Selecting Cluster based on social support score")
        cluster_scores = {cluster: 0.0 for cluster in clusters}

        for cluster in clusters:
            # social support
            sosu_ranker_scores = self.sosu_ranker.score_users(cluster.users)
            sosu_ranking = list(
                sorted(sosu_ranker_scores, key=lambda x: (sosu_ranker_scores[x][0], sosu_ranker_scores[x][1]),
                       reverse=True))

            current_top_10_users = sosu_ranking[:10]

            cluster_scores[cluster] = \
                sum(self.community_social_support_ranker.score_users(previous_top_10_users,
                                                                     current_top_10_users).values())

        return max(cluster_scores, key=cluster_scores.get)

    def _clustering(self, user_id: str, user_activity: str, leaves: bool = False):
        """Returns clusters in descending order of size after refining using jaccard similarity
        (all pairs of users).
        """
        screen_name = self.user_getter.get_user_by_id(user_id).screen_name
        # Generate clusters from the friends of the user and refine them using Jaccard similarity
        # of the "friends" activity
        refined_clusters = bct.clustering_from_social_graph(screen_name, user_activity=user_activity, leaves=leaves)
        sorted_clusters = sorted(refined_clusters, key=lambda c: len(c.users), reverse=True)

        return sorted_clusters
