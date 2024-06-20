import os
import json
from src.process.data_cleaning.data_cleaning_distributions import jaccard_similarity
from src.model.user import User
from src.model.local_neighbourhood import LocalNeighbourhood
from typing import Dict
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

class CoreDetector():
    """
    Given an initial user, and a "community/topic", determine the core user of
    that community
    """

    def __init__(self, user_getter, user_downloader, user_friends_downloader,
            extended_friends_cleaner,
            local_neighbourhood_downloader,
            local_neighbourhood_tweet_downloader, local_neighbourhood_getter,
            tweet_processor, social_graph_constructor, clusterer, cluster_getter,
            cluster_word_frequency_processor, cluster_word_frequency_getter,
            prod_ranker, con_ranker, ranking_getter, user_tweet_downloader, user_tweet_getter,
                 user_friend_getter):
        self.user_getter = user_getter
        self.user_downloader = user_downloader
        self.user_friends_downloader = user_friends_downloader
        self.user_friend_getter = user_friend_getter
        self.user_tweet_downloader = user_tweet_downloader
        self.user_tweet_getter = user_tweet_getter
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
        self.prod_ranker = prod_ranker
        self.con_ranker = con_ranker
        self.ranking_getter = ranking_getter


    def detect_core_by_screen_name(self, screen_name: str):
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
        self.detect_core(user.id)

    def detect_core(self, initial_user_id: str, default_cluster=1):
        log.info("Beginning core detection algorithm for user with id " + str(initial_user_id))

        # prev_users = []
        curr_user_id = initial_user_id
        prev_user_id = None
        prev_wf_vectors = []
        curr_wf_vector = None
        prev_cluster = None
        while str(curr_user_id) != str(prev_user_id):

            prev_user_id = curr_user_id
            if curr_wf_vector is not None:
                prev_wf_vectors.append(curr_wf_vector)

            try:
                curr_user_id, curr_wf_vector, curr_cluster = self.loop(int(curr_user_id), prev_cluster,
                    prev_wf_vector=curr_wf_vector, default_cluster=default_cluster)
                prev_cluster = curr_cluster
            except Exception as e:
                log.exception(e)
                exit()

        log.info("The final user for initial user " + str(initial_user_id) + " is "
                 + self.user_getter.get_user_by_id(str(curr_user_id)).screen_name)


            # TODO: Add check for if wf vector is drifting

    def loop(self, user_id: str, prev_cluster, prev_wf_vector=None, default_cluster=1, v=True, skip_download=True):
        # downloaded_users = ["876274407995527169", "985158406125375488", "359831209"]
        downloaded_users = []

        if not skip_download or str(user_id) not in downloaded_users:
            # TODO Add flag for skipping download step
            log.info("Downloading User")
            self.user_downloader.download_user_by_id(user_id)

            log.info("Downloading User Tweets")
            self.user_tweet_downloader.download_user_tweets_by_user_id(str(user_id))

            log.info("Downloading User Friends")
            self.user_friends_downloader.download_friends_users_by_id(user_id)

            log.info("Cleaning Friends List by Global Attributes")
            user = self.user_getter.get_user_by_id(str(user_id))
            follower_thresh = 0.1 * user.followers_count
            friend_thresh = 0.1 * user.friends_count
            tweet_thresh = 0.1 * len(self.user_tweet_getter.get_tweets_by_user_id_time_restricted(str(user_id)))
            clean_list = self.extended_friends_cleaner.clean_friends_global(user_id,
                            tweet_threshold=tweet_thresh, follower_threshold=follower_thresh, friend_threshold=friend_thresh)

            log.info("Downloading Local Neighbourhood")
            self.local_neighbourhood_downloader.download_local_neighbourhood_by_id(user_id)

            log.info("Cleaning Friends List by Local Attributes")
            self.extended_friends_cleaner.clean_friends_local(user_id, clean_list)

            log.info("Updating Local Neighbourhood")
            self.local_neighbourhood_downloader.download_local_neighbourhood_by_id(user_id)

            # log.info("Downloading Local Neighbourhood Tweets")
            # self.local_neighbourhood_tweet_downloader.download_user_tweets_by_local_neighbourhood(user_id)

        log.info("Done downloading Beginning Processing")
        local_neighbourhood = self.local_neighbourhood_getter.get_local_neighbourhood(user_id)

        # Refined Friends Method
        log.info("Refining Friends List:")
        user_list = local_neighbourhood.get_user_id_list()
        friends_map = {}
        for user in user_list:
            friends_list = []
            friends = local_neighbourhood.get_user_friends(user)

            # print(len(friends))
            for friend in friends:
                if user in local_neighbourhood.get_user_friends(str(friend)):
                    friends_list.append(friend)
                if user == str(user_id):
                    if int(user) in self.user_friend_getter.get_user_friends_ids(str(friend)):
                        friends_list.append(friend)
            # print(len(friends_list))
            friends_map[user] = friends_list

        log.info("Refining by Jaccard Similarity:")
        for user in user_list:
            friends_list = friends_map[user]
            similarities = {}
            for friend in friends_list:
                sim = jaccard_similarity(friends_list, friends_map[str(friend)])
                similarities[friend] = sim
            sorted_users = sorted(similarities, key=similarities.get, reverse=True)
            top_sum = 0
            for top_user in sorted_users[:10]:
                top_sum += similarities[top_user]
            if len(sorted_users) >= 10:
                thresh = 0.1 * (top_sum / 10)
            elif len(sorted_users) == 0:
                thresh = 0
            else:
                thresh = 0.1 * (top_sum / len(sorted_users))
            # Can do more efficiently using binary search
            index = len(sorted_users)
            for i in range(len(sorted_users)):
                user = sorted_users[i]
                if similarities[user] < thresh:
                    index = i
                    break
            friends_map[user] = sorted_users[:index]

        log.info("Setting Local Neighborhood:")
        refined_local_neighborhood = LocalNeighbourhood(str(user_id), None, friends_map)
        social_graph = self.social_graph_constructor.construct_social_graph_from_local_neighbourhood(user_id, refined_local_neighborhood)
        log.info("Clustering:")
        clusters = self.clusterer.cluster_by_social_graph(user_id, social_graph, None)


        # log.info("Processing Local Neighbourhood Tweets")
        # self.tweet_processor.process_tweets_by_local_neighbourhood(local_neighbourhood)

        # log.info("Construct social graph")
        # self.social_graph_constructor.construct_social_graph(user_id)
        #
        # log.info("Performing Clustering")
        # self.clusterer.cluster(user_id, {"graph_type": "union"})
        # #self.clusterer.cluster_by_social_graph(user_id, social_graph, {"graph_type": "union"})
        # clusters, params = self.cluster_getter.get_clusters(user_id, params={"graph_type": "union"})

        curr_wf_vector = None

        # Cluster chosen using word vector similarity
        # if prev_wf_vector is not None:
        #     log.info("Picking Cluster")
        #
        #     scores = {}
        #     cluster_wf_vectors = []
        #     for i in range(len(clusters)):
        #         cluster = clusters[i]
        #
        #         self.cluster_word_frequency_processor.process_cluster_word_frequency_vector(cluster.users)
        #         cluster_wf_vector = self.cluster_word_frequency_getter.get_cluster_word_frequency_by_ids(cluster.users)
        #         cluster_wf_vectors.append(cluster_wf_vector)
        #
        #         scores[i] = cluster_wf_vector.word_frequency_vector.cosine_sim_to(prev_wf_vector.word_frequency_vector)
        #
        #     # Sort word frequency vectors by similarity
        #     sorted_wf_vectors = list(sorted(scores, key=scores.get, reverse=True))
        #     closest_index = sorted_wf_vectors[0]
        #
        #     curr_cluster = clusters[closest_index]
        #     curr_wf_vector = cluster_wf_vectors[closest_index]
        # else:
        #     log.info("Picking Default Cluster")
        #     cluster = clusters[0]
        #     self.cluster_word_frequency_processor.process_cluster_word_frequency_vector(cluster.users)
        #
        #     curr_cluster = cluster
        #     curr_wf_vector = self.cluster_word_frequency_getter.get_cluster_word_frequency_by_ids(cluster.users)

        # Cluster Using Jaccard Set Similarity
        if prev_cluster is not None:
            log.info("Picking Cluster")
            similarities = {}
            for i in range(len(clusters)):
                cluster = clusters[i]
                similarities[i] = jaccard_similarity(prev_cluster.users, cluster.users)

            # Sort Jaccard similarities
            log.info("Similarities: ")
            log.info(similarities)
            sorted_similarities = list(sorted(similarities, key=similarities.get, reverse=True))

            closest_index = sorted_similarities[0]

            curr_cluster = clusters[closest_index]

        else:
            log.info("Picking Default Cluster")
            largest_index = 0
            for i in range(len(clusters)):
                cluster = clusters[i]
                if len(cluster.users) > len(clusters[largest_index].users):
                    largest_index = i

            curr_cluster = clusters[largest_index]

        log.info("The cluster chosen is: ")
        log.info(curr_cluster.users)

        log.info("Downloading Cluster Tweets")
        if str(user_id) not in downloaded_users:
            self.user_tweet_downloader.stream_tweets_by_user_list(curr_cluster.users)
            #self.user_tweet_downloader.download_user_tweets_by_user_list(curr_cluster.users)

        log.info("Ranking Cluster")
        prod_ranking, prod = self.prod_ranker.rank(str(user_id), curr_cluster)
        con_ranking, con = self.con_ranker.rank(str(user_id), curr_cluster)

        # prod_ranking = self.ranking_getter.get_ranking(str(user_id), params="retweets")
        # con_ranking = self.ranking_getter.get_ranking(str(user_id), params="consumption utility")

        # local_retweets = []
        # for retweet in self.user_tweet_getter.get_retweets_by_user_id_time_restricted("254201259"):
        #     if str(retweet.retweet_user_id) in curr_cluster.users and str(retweet.retweet_user_id) != "254201259":
        #         local_retweets.append(retweet)
        # log.info(len(local_retweets))
        # count = 0
        # for retweet in local_retweets:
        #     if str(retweet.retweet_user_id) in set([str(id) for id in friends]).intersection(curr_cluster.users):
        #         count += 1
        #     else:
        #         if str(retweet.retweet_user_id) not in curr_cluster.users:
        #             print("nope!")
        #         log.info(retweet.retweet_user_id)
        # log.info(count/len(local_retweets))

        top_10_prod = prod_ranking.get_top_10_user_ids()
        top_10_con = con_ranking.get_top_10_user_ids()

        top_20_prod = prod_ranking.get_top_20_user_ids()
        top_20_con = con_ranking.get_top_20_user_ids()

        top_30_prod = prod_ranking.get_top_30_user_ids()
        top_30_con = con_ranking.get_top_30_user_ids()

        top_50_prod = prod_ranking.get_top_50_user_ids()
        top_50_con = con_ranking.get_top_50_user_ids()

        top_150_prod = prod_ranking.get_all_ranked_user_ids()[:150]
        top_150_con = con_ranking.get_all_ranked_user_ids()[:150]

        top_400_prod = prod_ranking.get_all_ranked_user_ids()[:400]
        top_400_con = con_ranking.get_all_ranked_user_ids()[:400]

        # top_30_prod = prod_ranking[:30]
        # top_30_con = con_ranking[:30]
        #
        # top_50_prod = prod_ranking[:50]
        # top_50_con = con_ranking[:50]

        intersection_10 = set(top_10_prod).intersection(top_10_con)
        intersection_10_prod = sorted(intersection_10, key=prod.get, reverse=True)
        intersection_10_con = sorted(intersection_10, key=con.get, reverse=True)

        intersection_20 = set(top_20_prod).intersection(top_20_con)
        intersection_20_prod = sorted(intersection_20, key=prod.get, reverse=True)
        intersection_20_con = sorted(intersection_20, key=con.get, reverse=True)

        intersection_30 = set(top_30_prod).intersection(top_30_con)
        intersection_30_prod = sorted(intersection_30, key=prod.get, reverse=True)
        intersection_30_con = sorted(intersection_30, key=con.get, reverse=True)

        intersection_50 = set(top_50_prod).intersection(top_50_con)
        intersection_50_prod = sorted(intersection_50, key=prod.get, reverse=True)
        intersection_50_con = sorted(intersection_50, key=con.get, reverse=True)

        intersection_150 = set(top_150_prod).intersection(top_150_con)
        intersection_150_prod = sorted(intersection_150, key=prod.get, reverse=True)
        intersection_150_con = sorted(intersection_150, key=con.get, reverse=True)

        intersection_400 = set(top_400_prod).intersection(top_400_con)
        intersection_400_prod = sorted(intersection_400, key=prod.get, reverse=True)
        intersection_400_con = sorted(intersection_400, key=con.get, reverse=True)


        log.info("Top 50 Prod")
        log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in top_50_prod])
        log.info("Top 50 Con")
        log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in top_50_con])

        log.info("Using Top 10: ")
        log.info("Production:")
        log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_10_prod])
        log.info("Consumption:")
        log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_10_con])

        log.info("Using Top 20: ")
        log.info("Production:")
        log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_20_prod])
        log.info("Consumption:")
        log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_20_con])

        # log.info("Using Top 30: ")
        # log.info("Production:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_30_prod])
        # log.info("Consumption:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_30_con])
        #
        # log.info("Using Top 50: ")
        # log.info("Production:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_50_prod])
        # log.info("Consumption:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_50_con])
        #
        # log.info("Using Top 150: ")
        # log.info("Production:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_150_prod])
        # log.info("Consumption:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_150_con])
        #
        # log.info("Using Top 400: ")
        # log.info("Production:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_400_prod])
        # log.info("Consumption:")
        # log.info([self.user_getter.get_user_by_id(str(id)).screen_name for id in intersection_400_con])

        # By Production
        log.info("By Production")
        curr_user_id = intersection_20_prod[0]

        if curr_user_id == str(user_id):
            if intersection_20_con[0] != curr_user_id:
                index = intersection_20_con.index(curr_user_id)
                for i in range(1, 20):
                    temp_id = intersection_20_prod[i]
                    if intersection_20_con.index(temp_id) < index:
                        curr_user_id = temp_id
                        break

        # By Consumption
        # log.info("By Consumption")
        # curr_user_id = intersection_20_con[0]
        #
        # if curr_user_id == str(user_id):
        #     if intersection_20_prod[0] != curr_user_id:
        #         index = intersection_20_prod.index(curr_user_id)
        #         for i in range(1, 20):
        #             temp_id = intersection_20_con[i]
        #             if intersection_20_prod.index(temp_id) < index:
        #                 curr_user_id = temp_id
        #                 break

        # curr_user_id = ranking.get_top_user_id()
        # top_ids = ranking.get_top_20_user_ids()
        # top_names = [self.user_getter.get_user_by_id(str(id)).screen_name for id in top_ids]
        # log.info("Top 20 users are: ")
        # log.info(top_names)
        curr_user_name = self.user_getter.get_user_by_id(str(curr_user_id)).screen_name
        log.info("Highest Ranking User is " + curr_user_name)
        # self.save_top_users(curr_cluster.users, top_names, self.user_getter.get_user_by_id(str(user_id)).screen_name, "production")

        return curr_user_id, curr_wf_vector, curr_cluster


    def save_top_users(self, cluster, users, seed_name, type):

        path = "./results/" + type + "/top_users/"

        if not os.path.exists(path):
            os.makedirs(path)
        filename = (path + seed_name + '.json')

        json_data = {
            'seed_name': seed_name,
            'top_20_users': users,
            'cluster': cluster
        }

        with open(filename, 'w+') as file:
            json.dump(json_data, file)

