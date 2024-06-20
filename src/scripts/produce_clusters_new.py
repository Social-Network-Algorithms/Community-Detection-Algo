import os
import sys

from src.process.data_cleaning.data_cleaning_distributions import jaccard_similarity
import argparse
import time
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from src.model.local_neighbourhood import LocalNeighbourhood
import json
import logging
import random
import gc

log = LoggerFactory.logger(__name__, logging.ERROR)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/default_config.yaml"


def produce_plots(user_name: str, thresh, iteration, path=DEFAULT_PATH):

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    user_friend_getter = dao_module.get_user_friend_getter()
    friends_cleaner = process_module.get_extended_friends_cleaner()
    social_graph_constructor = process_module.get_social_graph_constructor()
    clusterer = process_module.get_clusterer()
    user_getter = dao_module.get_user_getter()
    user_tweet_getter = dao_module.get_user_tweet_getter()
    clean_user_friend_getter = dao_module.get_cleaned_user_friend_getter()
    local_neighbourhood_getter = dao_module.get_local_neighbourhood_getter()
    prod_ranker = process_module.get_ranker()
    con_ranker = process_module.get_ranker("Consumption")

    seed_id = user_getter.get_user_by_screen_name(user_name).id
    # Full user friend list
    init_user_friends = user_friend_getter.get_user_friends_ids(seed_id)
    # tweet_processor.process_tweets_by_user_list(init_user_friends)

    # user = user_getter.get_user_by_id(str(seed_id))
    # follower_thresh = 0.1 * user.followers_count
    # friend_thresh = 0.1 * user.friends_count
    # tweet_thresh = 0.1 * len(user_tweet_getter.get_tweets_by_user_id_time_restricted(str(seed_id)))
    # global_clean = friends_cleaner.clean_friends_global(seed_id,
    #             tweet_threshold=tweet_thresh, follower_threshold=follower_thresh, friend_threshold=friend_thresh)
    # clean_list, removed_list = friends_cleaner.clean_friends_local(seed_id, global_clean, local_following=thresh)
    # clean_list = [str(id) for id in clean_list]

    clean_list = clean_user_friend_getter.get_user_friends_ids(str(seed_id))
    # social_graph = social_graph_constructor.construct_social_graph(seed_id, is_union=False)
    # following_counts = {}
    # for user_id in clean_list:
    #     friends = user_friend_getter.get_user_friends_ids(str(user_id))
    #     following_counts[user_id] = len(set(friends).intersection(clean_list))
    # sorted_users = list(sorted(following_counts, key=following_counts.get, reverse=True))
    # print([following_counts[user] for user in sorted_users])

    local_neighbourhood = local_neighbourhood_getter.get_local_neighbourhood(seed_id)

    # Refined Friends Method
    for k in range(1, 7):
        log.info("Refining Friends List:")
        user_list = local_neighbourhood.get_user_id_list()
        friends_map = {}
        print('1012256833816363008' in user_list)
        for user in user_list:
            friends_list = []
            friends = local_neighbourhood.get_user_activities(user)
            # print(len(friends))
            for friend in friends:
                if user in local_neighbourhood.get_user_activities(str(friend)):
                    friends_list.append(str(friend))
                if user == str(seed_id):
                    if int(user) in user_friend_getter.get_user_friends_ids(str(friend)):
                        friends_list.append(str(friend))
            # print(len(friends_list))
            friends_map[str(user)] = friends_list
            if user == "254201259":
                print(len(friends_list))

        log.info("Refining by Jaccard Similarity:")
        for user in [str(id) for id in user_list]:
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
                thresh = 0.1 * k * (top_sum / 10)
            elif len(sorted_users) == 0:
                thresh = 0
            else:
                thresh = 0.1 * k * (top_sum / len(sorted_users))
            # Can do more efficiently using binary search
            index = len(sorted_users)
            for i in range(len(sorted_users)):
                user = sorted_users[i]
                if similarities[user] < thresh:
                    index = i
                    break
            friends_map[user] = sorted_users[:index]

        log.info("Thresh: " + str(0.1*k))
        log.info("Setting Local Neighborhood:")
        refined_local_neighborhood = LocalNeighbourhood(str(seed_id), None, friends_map)
        social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(seed_id, refined_local_neighborhood, is_union=False)
        log.info("Clustering:")
        clusters = clusterer.cluster_by_social_graph(seed_id, social_graph, None)
        # log.info("Iteration: " + str(iteration))
        log.info(len(clusters))
        cluster_sizes = {}
        for i in range(len(clusters)):
            cluster_sizes[i] = len(clusters[i].users)
        sorted_indices = sorted(cluster_sizes, key=cluster_sizes.get, reverse=True)
        for index in sorted_indices[:5]:
            cluster = clusters[index]
            prod_ranking, prod = prod_ranker.rank(str(seed_id), cluster)
            con_ranking, con = con_ranker.rank(str(seed_id), cluster)
            ranked_prod = prod_ranking.get_all_ranked_user_ids()
            ranked_con = con_ranking.get_all_ranked_user_ids()

            log.info("Cluster Size: " + str(len(cluster.users)))
            log.info("Ranked by Production: ")
            log.info([user_getter.get_user_by_id(str(id)).screen_name for id in ranked_prod])
            log.info("Ranked by Consumption: ")
            log.info([user_getter.get_user_by_id(str(id)).screen_name for id in ranked_con])
        # for cluster in clusters:
        #     if 10 < len(cluster.users) < 1000:
        #         log.info("Cluster Size: " + str(len(cluster.users)))
        #         log.info([user_getter.get_user_by_id(str(id)).screen_name for id in cluster.users])

    # for i in range(3):
    #     num = 50 * (2**i)
    #     log.info(num)
    #     init_user_dict = get_local_neighbourhood_user_dict(seed_id, sorted_users[:num], user_friend_getter)
    #     print("next!")
    #     local_neighbourhood = LocalNeighbourhood(seed_id=seed_id, params=None, users=init_user_dict)
    #     print("next!")
    #     social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(seed_id,
    #                                                                                             local_neighbourhood, is_union=False)
    #     print("next!")
    #     clusters = clusterer.cluster_by_social_graph(seed_id, social_graph, social_graph.params)
    #     log.info("Iteration: " + str(i))
    #     log.info(len(clusters))

    # for cluster in clusters:
    #     log.info([user_getter.get_user_by_id(str(id)).screen_name for id in cluster.users])
    # write_clusters_to_file(user_name, clusters, i, thresh, "local_and_global")


def write_clusters_to_file(user_name, clusters, i, thresh, type):
    path = "./dc2_exp/" + type + "/clusters_local_" + str(thresh)

    if not os.path.exists(path):
        os.makedirs(path)
    filename = ("./dc2_exp/" + type + "/clusters_local_" + str(thresh) + "_global_50" + str("/") + user_name + '_clusters_' + str(i) + '.json')
    user_lists = [cluster.users for cluster in clusters]
    for j in range(len(clusters)):
        log.info(len(clusters[j].users))

    with open(filename, 'w+') as file:
        json.dump(user_lists, file)


def get_local_neighbourhood_user_dict(seed_id, init_user_friends, user_friend_getter):
    user_dict = {}

    user_dict[str(seed_id)] = init_user_friends

    for curr_id in init_user_friends:
        curr_user_friends = user_friend_getter.get_user_friends_ids(curr_id)
        curr_user_friends = [str(id) for id in curr_user_friends if (id in init_user_friends)]
        user_dict[str(curr_id)] = curr_user_friends

    return user_dict


if __name__ == "__main__":
    """
    Short script to produce scatter plots
    """
    parser = argparse.ArgumentParser(description='Short script to produce scatter plots of utility')

    parser.add_argument('-n', '--screen_name', dest='name',
                        help="The screen name of the user to download", required=True)
    parser.add_argument('-p', '--path', dest='path', required=False,
                        default=DEFAULT_PATH, help='The path of the config file', type=str)
    parser.add_argument('-t', '--thresh', dest='thresh', required=False,
                        default=DEFAULT_PATH, help='thresh', type=float)
    parser.add_argument('-j', '--iter', dest='j', required=False,
                        default=DEFAULT_PATH, help='Iteration', type=int)

    args = parser.parse_args()

    produce_plots(args.name, args.thresh, args.j)
    # if args.j < 5:
    #     new_arg = sys.argv
    #     iteration = args.j
    #     new_arg[6] = str(iteration + 1)
    #     os.execv(sys.executable, ['python'] + sys.argv)
