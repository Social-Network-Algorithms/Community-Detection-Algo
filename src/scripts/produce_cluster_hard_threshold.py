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

def produce_plots(seed_id: str, user_name: str, threshold: int, i, type, path=DEFAULT_PATH):
    threshold = int(threshold)
    if type == 0:
        type_str = "default"
        t1 = threshold
        t2 = threshold
    elif type == 1:
        type_str = "follower_only"
        t1 = 0
        t2 = threshold
    elif type == 2:
        type_str = "tweet_only"
        t1 = threshold
        t2 = 0

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    user_friend_getter = dao_module.get_user_friend_getter()
    friends_cleaner = process_module.get_friends_cleaner()
    social_graph_constructor = process_module.get_social_graph_constructor()
    clusterer = process_module.get_clusterer()

    # Full user friend list
    init_user_friends = user_friend_getter.get_user_friends_ids(seed_id)
    # tweet_processor.process_tweets_by_user_list(init_user_friends)
    clean_list = friends_cleaner.clean_friends_from_list_hard_thresh(seed_id, init_user_friends, t1, t2)
    clean_list = [str(id) for id in clean_list]
    init_user_dict = get_local_neighbourhood_user_dict(seed_id, clean_list, user_friend_getter)
    local_neighbourhood = LocalNeighbourhood(seed_id=seed_id, params=None, users=init_user_dict)
    social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(seed_id, local_neighbourhood, remove_unconnected_nodes=False)

    clusters = clusterer.cluster_by_social_graph(seed_id, social_graph, {})
    write_clusters_to_file(user_name, clusters, i, threshold, type_str)

def write_clusters_to_file(user_name, clusters, i, threshold, type):
    filename = ("./dc3_exp/" + type + "/clusters_" + str(threshold) + str("/") + user_name + '_clusters_' + str(i) + '.json')
    user_lists = [cluster.users for cluster in clusters]
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
    parser.add_argument('-i', '--seed_id', dest='id',
        help="The id of the user to download", required=True)
    parser.add_argument('-n', '--screen_name', dest='name',
        help="The screen name of the user to download", required=True)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)
    parser.add_argument('-j', '--iter', dest='j', required=False,
        default=DEFAULT_PATH, help='Iteration', type=str)
    parser.add_argument('-t', '--thresh', dest='thresh', required=False,
        default=DEFAULT_PATH, help='thresh', type=str)
    parser.add_argument('-s', '--type', dest='type', required=False,
        default=DEFAULT_PATH, help='type', type=int)

    args = parser.parse_args()

    produce_plots(args.id, args.name, args.thresh, args.j, args.type)
