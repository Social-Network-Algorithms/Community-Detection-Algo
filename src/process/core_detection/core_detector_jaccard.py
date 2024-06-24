from src.shared.logger_factory import LoggerFactory
import src.clustering_experiments.create_social_graph_and_cluster as csgc
import src.clustering_experiments.build_cluster_tree as bct
from src.clustering_experiments.ranking_users_in_clusters import rank_users, get_new_intersection_ranking, \
    get_simple_prod_ranking, get_simple_con_ranking, get_simple_followers_ranking

log = LoggerFactory.logger(__name__)


class JaccardCoreDetector():
    """
    Given an initial user, and a "community/topic", determine the core user of
    that community
    """

    def __init__(self, user_getter, user_downloader, user_friends_downloader,
            extended_friends_cleaner,
            local_neighbourhood_downloader,
            local_neighbourhood_tweet_downloader, local_neighbourhood_getter,
            tweet_processor, social_graph_constructor, clusterer, cluster_getter,
            cluster_word_frequency_processor, cluster_word_frequency_getter, follower_ranker,
            prod_ranker, con_ranker, sosu_ranker, ranking_getter, user_tweet_downloader, user_tweets_getter,
                 user_friend_getter):
        self.user_getter = user_getter
        self.user_downloader = user_downloader
        self.user_friends_downloader = user_friends_downloader
        self.user_friend_getter = user_friend_getter
        self.user_tweet_downloader = user_tweet_downloader
        self.user_tweets_getter = user_tweets_getter
        self.extended_friends_cleaner = extended_friends_cleaner
        self.local_neighbourhood_downloader = local_neighbourhood_downloader
        self.local_neighbourhood_tweet_downloader = local_neighbourhood_tweet_downloader
        self.local_neighbourhood_getter = local_neighbourhood_getter
        self.tweet_processor = tweet_processor
        self.social_graph_constructor = social_graph_constructor
        self.clusterer = clusterer
        self.cluster_getter = cluster_getter
        self.cluster_word_frequency_processor = cluster_word_frequency_processor
        self.cluster_word_frequency_getter = cluster_word_frequency_getter
        self.follower_ranker = follower_ranker
        self.prod_ranker = prod_ranker
        self.con_ranker = con_ranker
        self.sosu_ranker = sosu_ranker
        self.ranking_getter = ranking_getter

    def detect_core_by_screen_name(self, screen_name: str, user_activity:str, skip_download=True, optimize_threshold=False):
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
        self.detect_core(user.id, user_activity, skip_download, optimize_threshold)

    def detect_core(self, initial_user_id: str, user_activity: str, skip_download=True, optimize_threshold=False):
        log.info("Beginning core detection algorithm for user with id " + str(initial_user_id))

        prev_user_id = [str(initial_user_id)]
        curr_user_id = None
        top_10_users = []
        top_10 = []
        clusters = []
        # First iteration
        i = 0
        try:
            i += 1
            curr_user_id, top_10_users, cluster = self.first_iteration(prev_user_id[0], user_activity, skip_download, optimize_threshold)
            top_10.append(top_10_users)
            clusters.append(cluster)
        except Exception as e:
            log.exception(e)
            exit()
        # self._visualize_cluster(top_10_users, cluster, user_activity)
        # Other iterations
        while str(curr_user_id) not in prev_user_id:
            log.info("Curr user id: " + str(curr_user_id))
            log.info(f"Prev users list: {prev_user_id}")
            prev_user_id.append(str(curr_user_id))

            try:
                i += 1
                curr_user_id, top_10_users, cluster = self.loop_iteration(curr_user_id, user_activity, top_10_users, i, skip_download, optimize_threshold)
                top_10.append(top_10_users)
                clusters.append(cluster)
            except Exception as e:
                log.exception(e)
                exit()

        # Save selected clusters to file
        # with open(f"results_data/selected_clusters_{initial_user_id}_uw.pkl", "wb") as f:
        #     pickle.dump(clusters, f)
        # with open(f"data/selected_clusters_{initial_user_id}_ww_friends", "wb") as f:
        #     pickle.dump(clusters, f)
        log.info("The previous user id list is " + str(prev_user_id))
        log.info("The final user for initial user " + str(initial_user_id) + " is "
                 + self.user_getter.get_user_by_id(str(curr_user_id)).screen_name)
        # This is the core
        log.info(f"The top 10 users for the selected cluster in the last iteration were: {top_10_users}")
        log.info(f"The top 10 users for the selected cluster in each iteration were:")
        for top in top_10:
            log.info(top)
        log.info(f"The selected cluster in each iteration were:")
        for cluster in clusters:
            users = [self.user_getter.get_user_by_id(user).screen_name for user in cluster.users]
            log.info(users)

    def first_iteration(self, user_id: str, user_activity:str, skip_download=True, optimize_threshold=False):
        if not skip_download:
            self._download(user_id)

        screen_name = self.user_getter.get_user_by_id(user_id).screen_name

        if optimize_threshold:
            thresh = self._pick_optimal_threshold(user_id, user_activity, iter=1)
        else:
            thresh = 0.4
        clusters = self._clustering(user_id, user_activity, thresh, iter=1)
        # log.info("Saving initial clusters to file")
        # Save initial clusters to file
        # with open(f"initial_clusters_{screen_name}", "wb") as f:
        #     pickle.dump(clusters, f)

        chosen_cluster = self._user_select_cluster(user_id, clusters)
        # chosen_cluster = self._auto_select_first_cluster(user_id, clusters)
        if not skip_download:
            self._download_cluster_tweets(chosen_cluster)
        top_10_users = rank_users(screen_name, chosen_cluster) if chosen_cluster.top_users is None else chosen_cluster.top_users
        log.info("top_10 of chosen cluster:")
        log.info(top_10_users)
        curr_user = self.user_getter.get_user_by_screen_name(top_10_users[0])
        curr_user = curr_user.id

        return curr_user, top_10_users, chosen_cluster

    def _user_select_cluster(self, user_id, clusters):
        """User chooses cluster."""
        use_id = True
        cluster_id_map = {clusters[i].id: i for i in range(len(clusters))}
        log.info(f"Here are the {len(clusters)} clusters that have been created:")
        # If None in key
        if None in cluster_id_map:
            use_id = False
        for i in range(len(clusters)):
            log.info(f"All users in Cluster id={clusters[i].id if use_id else i}:")
            readable_users = [self.user_getter.get_user_by_id(user_id).screen_name for user_id in clusters[i].users]
            log.info(readable_users)
            log.info(f"Top_10 users in Cluster id={clusters[i].id if use_id else i} before we download their tweets:")
            screen_name = self.user_getter.get_user_by_id(user_id).screen_name
            top_10_users = rank_users(screen_name, clusters[i]) if clusters[i].top_users is None else clusters[i].top_users
            log.info(top_10_users)
            log.info("")
        while True:
            try:
                i = str(input("Please input the id of the cluster you choose to explore:"))
                if use_id and i in cluster_id_map:
                    break
                elif not use_id and 0 <= int(i) < len(clusters):
                    break
                else:
                    print("Invalid input. Please enter a number associated to the cluster you want to choose")
            except ValueError:
                print("Invalid input. Please enter a number associated to the cluster you want to choose")
        log.info(f"The user chooses cluster {i}")
        selected_cluster = clusters[cluster_id_map[i]] if use_id else clusters[int(i)]
        return selected_cluster

    def loop_iteration(self, user_id: str, user_activity, curr_top_10_users, iter, skip_download=True, optimize_threshold=False):
        if not skip_download:
            self._download(user_id)

        screen_name = self.user_getter.get_user_by_id(user_id).screen_name

        if optimize_threshold:
            thresh = self._pick_optimal_threshold(user_id, user_activity, iter)
        else:
            thresh = 0.4
        clusters = self._clustering(user_id, user_activity, thresh, iter=iter)
        # clusters only keeps the largest intact ones, as in the report
        # now it selects by production utility
        chosen_cluster = self._select_cluster2(user_id, curr_top_10_users, clusters)
        log.info("The algorithm chooses cluster...")
        if chosen_cluster.id is None:
            log.info("Cluster index: " + str(clusters.index(chosen_cluster)))
        else:
            log.info("Cluster id: " + str(chosen_cluster.id))
        # Alternatively, the user can choose the cluster
        # chosen_cluster = self._user_select_cluster(user_id, clusters)
        if not skip_download:
            self._download_cluster_tweets(chosen_cluster)
        top_10_users = rank_users(screen_name, chosen_cluster) if chosen_cluster.top_users is None else chosen_cluster.top_users
        curr_user = self.user_getter.get_user_by_screen_name(top_10_users[0])
        curr_user = curr_user.id

        return curr_user, top_10_users, chosen_cluster
    
    def _auto_select_first_cluster(self, user_id, clusters):
        """Returns the cluster where the sum of the production utilities of the top 10 users of
        the previous iteration is the highest."""
        log.info(f"Here are the {len(clusters)} clusters that have been created:")
        cluster_scores = {cluster: 0.0 for cluster in clusters}
        screen_name = self.user_getter.get_user_by_id(user_id).screen_name
        for i in range(len(clusters)):
            log.info(f"All users in Cluster {i}:")
            readable_users = [self.user_getter.get_user_by_id(user_id).screen_name
                              for user_id in clusters[i].users]
            log.info(readable_users)
            log.info(f"Top_10 users in Cluster {i} before we download their tweets:")
            top_10_users = rank_users(screen_name, clusters[i])
            log.info(top_10_users)
            log.info("")

        log.info("Selecting Cluster based on production utilities")

        for cluster in cluster_scores:
            sosu, infl1, intersection_ranking = get_new_intersection_ranking(screen_name, cluster)
            if len(intersection_ranking) > 0:
                cluster_scores[cluster] = sum([sosu[str(user_id)][0] for user_id in intersection_ranking]) / len(intersection_ranking)
            else: 
                cluster_scores[cluster] = 0

        index = clusters.index(max(cluster_scores, key=cluster_scores.get))
        log.info(f"Cluster {index} has been chosen\n")
        return clusters[index]

    def _select_cluster(self, user_id, top_10_users, clusters):
        """Returns the cluster where the sum of the production utilities of the top 10 users of
        the previous iteration is the highest."""
        log.info("Selecting Cluster based on production utilities")

        cluster_scores = {cluster: 0 for cluster in clusters}
        top_10_users_ids = [self.user_getter.get_user_by_screen_name(top_user).id for top_user in top_10_users]

        for cluster in clusters:
            cluster_user_ids = list(set([str(user_id) for user_id in cluster.users + top_10_users_ids]))
            prod_ranker_scores = self.prod_ranker.score_users(cluster_user_ids)

            cluster_scores[cluster] = sum([prod_ranker_scores[str(user_id)][0] for user_id in top_10_users_ids])

        return max(cluster_scores, key=cluster_scores.get)
    
    def _select_cluster1(self, user_id, top_10_users, clusters):
        """Returns the cluster where the sum of the social support score of the top 10 users of the previous iteration is the highest."""

        log.info("Selecting Cluster based on social support")

        cluster_scores = {cluster: 0 for cluster in clusters}
        top_10_users_ids = [self.user_getter.get_user_by_screen_name(top_user).id for top_user in top_10_users]

        for cluster in clusters:
            cluster_user_ids = list(set([str(user_id) for user_id in cluster.users + top_10_users_ids]))
            sosu_ranker_scores = self.sosu_ranker.score_users(cluster_user_ids)

            cluster_scores[cluster] = sum([sosu_ranker_scores[str(user_id)][0] for user_id in top_10_users_ids])

        return max(cluster_scores, key=cluster_scores.get)
    
    def _select_cluster2(self, user_id, top_10_users, clusters):
        """Returns the cluster where the modified Jaccard similarity with the top 10 users of the previous iteration is the highest."""
        log.info("Selecting Cluster based on modified Jaccard similarity")
        screen_name = self.user_getter.get_user_by_id(user_id).screen_name
        cluster_scores = {cluster: 0.0 for cluster in clusters}
        top_10_users_ids = [self.user_getter.get_user_by_screen_name(top_user).id for top_user in top_10_users]

        for cluster in clusters:
            # social support
            sosu_ranker_scores = self.sosu_ranker.score_users(cluster.users)
            sosu_ranking = list(sorted(sosu_ranker_scores, key=lambda x: (sosu_ranker_scores[x][0], sosu_ranker_scores[x][1]), reverse=True))

            # production
            # prod_ranker_scores, _, _ = get_simple_prod_ranking(screen_name, cluster)
            # prod_ranking = list(sorted(prod_ranker_scores, key=lambda x: (prod_ranker_scores[x][0], prod_ranker_scores[x][1]), reverse=True))
            # cluster_scores[cluster] = sum([prod_ranker_scores[str(user_id)][0] for user_id in prod_ranking])

            # consumption
            # con_ranker_scores, _, _ = get_simple_con_ranking(screen_name, cluster)
            # con_ranking = list(sorted(con_ranker_scores, key=lambda x: (con_ranker_scores[x][0], con_ranker_scores[x][1]), reverse=True))
            # cluster_scores[cluster] = sum([con_ranker_scores[str(user_id)][0] for user_id in con_ranking])

            # local followers
            # local_followers_scores, _, _ = get_simple_followers_ranking(screen_name, cluster)
            # local_followers_ranking = list(sorted(local_followers_scores, key=lambda x: (local_followers_scores[x]), reverse=True))
            # cluster_scores[cluster] = sum([local_followers_scores[str(user_id)]for user_id in local_followers_ranking])

            # social support + influence 1
            # sosu, infl1, intersection_ranking = get_new_intersection_ranking(screen_name, cluster)
            # cluster_scores[cluster] = sum([sosu[str(user_id)][0] for user_id in intersection_ranking])

            # production + influence 1
            # prod, infl1, intersection_ranking = get_simple_prod_ranking(screen_name, cluster)
            # cluster_scores[cluster] = sum([prod[str(user_id)][0] for user_id in intersection_ranking])

            # consumption + influence 1
            # con, infl1, intersection_ranking = get_simple_con_ranking(screen_name, cluster)
            # cluster_scores[cluster] = sum([con[str(user_id)][0] for user_id in intersection_ranking])

            # local followers + influence 1
            # local_followers, infl1, intersection_ranking = get_simple_followers_ranking(screen_name, cluster)
            # cluster_scores[cluster] = sum([local_followers[str(user_id)] for user_id in intersection_ranking])

            for i, user_id in enumerate(top_10_users_ids):
                if user_id in sosu_ranking:
                    distance = abs(i - sosu_ranking.index(user_id))
                    weight = 1 / (i + 1) # higher ranked users are more important
                    cluster_scores[cluster] += weight / (distance + 1)

            cluster_scores[cluster] /= len(cluster.users)

        return max(cluster_scores, key=cluster_scores.get)

    def _download(self, user_id: str, clean=False):
            # TODO: Add a separate option for cleaning when not downloading
            user_id = int(user_id)
            screen_name = self.user_getter.get_user_by_id(str(user_id)).screen_name

            log.info(f"Downloading User {screen_name} {user_id}")
            self.user_downloader.download_user_by_id(user_id)

            log.info("Downloading User Tweets")
            self.user_tweet_downloader.download_user_tweets_by_user_id(user_id)

            log.info("Downloading User Friends")
            self.user_friends_downloader.download_friends_users_by_id(user_id)

            log.info("Downloading Local Neighbourhood")
            self.local_neighbourhood_downloader.download_local_neighbourhood_by_id(user_id)

            if clean:
                self._clean(user_id)
                log.info("Updating Local Neighbourhood")
                self.local_neighbourhood_downloader.download_local_neighbourhood_by_id(user_id)

            log.info("Done downloading. Beginning processing")

    def _clean(self, user_id, local_following=4):
        """Removes users based on global and local attributes."""
        clean_list = self._clean_globally(user_id)
        log.info("Cleaning Friends List by Local Attributes")
        self.extended_friends_cleaner.clean_friends_local(user_id, clean_list, local_following=local_following)

    def _clean_globally(self, user_id):
        """Removes users based on global follower, friend and tweet thresholds."""
        user = self.user_getter.get_user_by_id(str(user_id))
        log.info("Cleaning Friends List by Global Attributes")
        follower_thresh = 0.1 * user.followers_count
        friend_thresh = 0.1 * user.friends_count
        tweet_thresh = 0.1 * len(self.user_tweets_getter.get_tweets_by_user_id_time_restricted(str(user_id)))
        clean_list = self.extended_friends_cleaner.clean_friends_global(user_id,
                     tweet_threshold=tweet_thresh, follower_threshold=follower_thresh, friend_threshold=friend_thresh)

        return clean_list

    def _download_cluster_tweets(self, cluster):
        self.user_tweet_downloader.stream_tweets_by_user_list(cluster.users)

    def _clustering(self, user_id: str, user_activity:str,threshold: float=0.3, iter: int = 1):
        """Returns clusters in descending order of size after refining using jaccard similarity
        (all pairs of users).
        """
        screen_name = self.user_getter.get_user_by_id(user_id).screen_name

        # social_graph, local_neighbourhood = csgc.create_social_graph(screen_name)
        # refined_social_graph = csgc.refine_social_graph_jaccard_users(screen_name, social_graph, local_neighbourhood, threshold=threshold)
        # refined_clusters = csgc.clustering_from_social_graph(screen_name, refined_social_graph)
        refined_clusters = bct.clustering_from_social_graph(screen_name, user_activity=user_activity, iter=iter)
        # Remove clusters with less than SIZE_THRESHOLD users
        # refined_clusters = [cluster for cluster in refined_clusters if len(cluster.users) >= SIZE_THRESHOLD]
        sorted_clusters = sorted(refined_clusters, key=lambda c: len(c.users), reverse=True)

        return sorted_clusters

    def _pick_optimal_threshold(self, user_id: str, user_activity: str, iter: int):
        """Returns the optimal threshold for clustering for a given user."""
        log.info("---PICKING THRESHOLD NOW---")
        candidate_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]

        num_large_clusters = []
        for thresh in candidate_thresholds:
            large_clusters = csgc.discard_small_clusters(self._clustering(user_id, user_activity, thresh, iter))
            num_large_clusters.append(large_clusters)

        curr_num, curr_thresh = 0, 0
        for i in range(len(num_large_clusters)):
            if num_large_clusters[i] > curr_num:
                curr_num = num_large_clusters[i]
                curr_thresh = candidate_thresholds[i]
            elif num_large_clusters[i] == curr_num:
                pass
            else:  # Number of large clusters is decreasing now
                break

        log.info("---FINISHED PICKING THRESHOLD---")
        return curr_thresh
