import os
import sys

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


def produce_plots(user_name: str, thresh, i, path=DEFAULT_PATH):

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    user_friend_getter = dao_module.get_user_friend_getter()
    friends_cleaner = process_module.get_extended_friends_cleaner()
    social_graph_constructor = process_module.get_social_graph_constructor()
    clusterer = process_module.get_clusterer()
    user_getter = dao_module.get_user_getter()

    seed_id = user_getter.get_user_by_screen_name(user_name).id
    # Full user friend list
    init_user_friends = user_friend_getter.get_user_friends_ids(seed_id)
    # tweet_processor.process_tweets_by_user_list(init_user_friends)

    type = 'local_and_global'
    filename_start = "./dc2_exp/" + str(type) + '/clusters_local_' + str(thresh) + '_global_50' '/' + str(user_name) + '_clusters_'
    filename = filename_start + str(i) + '.json'
    with open(filename, 'r') as file:
        user_lists = json.load(file)
        count = len(user_lists)
    max_cluster = user_lists[0]
    for j in range(1, count):
        if len(user_lists[j]) > len(max_cluster):
            max_cluster = user_lists[j]
    max_cluster.remove(str(seed_id))
    log.info("Num users in max cluster is " + str(len(max_cluster)))
    init_user_dict = get_local_neighbourhood_user_dict(seed_id, max_cluster, user_friend_getter)
    local_neighbourhood = LocalNeighbourhood(seed_id=seed_id, params=None, users=init_user_dict)
    social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(seed_id, local_neighbourhood, remove_unconnected_nodes=True)
    clusters = clusterer.cluster_by_social_graph(seed_id, social_graph, {})

    log.info("Iteration: " + str(i))
    write_clusters_to_file(user_name, clusters, i, thresh, "local_and_global_of_cluster")


def write_clusters_to_file(user_name, clusters, i, thresh, type):
    path = "./dc2_exp/" + type + "/clusters_local_" + str(thresh) + "_global_50"

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
        curr_user_friends = [str(id) for id in curr_user_friends if (str(id) in init_user_friends)]
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
    if args.j < 19:
        new_arg = sys.argv
        iteration = args.j
        new_arg[6] = str(iteration + 1)
        os.execv(sys.executable, ['python'] + sys.argv)
