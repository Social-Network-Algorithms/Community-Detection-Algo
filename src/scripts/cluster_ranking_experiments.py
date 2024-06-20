import os
import sys

import networkx as nx

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

def ranking_distribution(user_name: str, thresh, path=DEFAULT_PATH):

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    production_ranker = process_module.get_ranker()
    consumption_ranker = process_module.get_ranker("Consumption")
    local_followers_ranker = process_module.get_ranker("LocalFollowers")
    relative_production_ranker = process_module.get_ranker("RelativeProduction")

    user_getter = dao_module.get_user_getter()
    friends_getter = dao_module.get_user_friend_getter()
    tweet_getter = dao_module.get_user_tweet_getter()
    clusterer = process_module.get_clusterer()

    seed_id = user_getter.get_user_by_screen_name(user_name).id
    type = 'local_and_global'
    filename = "./dc2_exp/" + str(type) + '/clusters_local_' + str(thresh) + '_global_50' '/' + str(user_name) + '_clusters_0.json'
    with open(filename, 'r') as file:
        user_lists = json.load(file)
        count = len(user_lists)

    cluster1 = user_lists[0]
    #similarity_retweets_matrix(user_name, thresh, 1, tweet_getter, cluster1)
    #similarity_matrix(user_name, thresh, 1, 'p', 'p', friends_getter, cluster1)
    #similarity_graph(user_name, seed_id, thresh, 1, friends_getter, cluster1, clusterer)

    for i in range(count):

        cluster = user_lists[i]
        log.info(len(cluster))

        log.info('Scoring Consumption...')
        consumption = consumption_ranker.score_users(cluster)
        ranked_consumption = list(sorted(consumption, key=consumption.get, reverse=True))
        consumptions = [consumption[user] for user in ranked_consumption]

        log.info('Scoring Production...')
        production = production_ranker.score_users(cluster)
        ranked_production = list(sorted(production, key=production.get, reverse=True))
        productions = [production[user] for user in ranked_production]

        log.info('Scoring Local Followers...')
        local_followers = local_followers_ranker.score_users(cluster)
        log.info(local_followers)
        ranked_followers = list(sorted(local_followers, key=local_followers.get, reverse=True))
        followers = [local_followers[user] for user in ranked_followers]

        log.info('Scoring Relative Production...')
        relative_production = relative_production_ranker.score_users(cluster)
        ranked_relative_production = list(sorted(relative_production, key=relative_production.get, reverse=True))



        titles = ['Distribution of Consumption at Local Threshold '
                  + str(thresh) + ' for Cluster ' + str(i+1), 'Distribution of Production at Local Threshold '
                  + str(thresh) + ' for Cluster ' + str(i+1),
                  'Distribution of Local Followers at Local Threshold ' + str(thresh) + ' for Cluster ' + str(i+1)]

        title = titles[0]
        plt.bar(ranked_consumption, consumptions)
        plt.ylabel('Consumption Utility')
        plt.xlabel('Users in Cluster')
        plt.title(title)
        plt.show()

        title = titles[1]
        plt.bar(ranked_production, productions)
        plt.ylabel('Production Utility')
        plt.xlabel('Users in Cluster')
        plt.title(title)
        plt.show()

        title = titles[2]
        plt.bar(ranked_followers, followers)
        plt.ylabel('Local Followers')
        plt.xlabel('Users in Cluster')
        plt.title(title)
        plt.show()

        compare_top_users(ranked_consumption, ranked_production, ranked_followers, ranked_relative_production, i+1, thresh, user_getter)


def compare_top_users(consumption, production, local_followers, relative_production, cluster_num, thresh, user_getter):
    for i in range(1, 3):
        top_consumption = consumption[:5*i]
        log.info(top_consumption)
        top_production = production[:5*i]
        log.info(top_production)
        top_followers = local_followers[:5*i]
        log.info(top_followers)
        top_rel_production = relative_production[:5*i]
        log.info(top_rel_production)
        # Take production to be reference set
        similarities = []
        # consumption_sim = jaccard_similarity(top_production, top_consumption)
        # similarities.append(consumption_sim)
        # followers_sim = jaccard_similarity(top_production, top_followers)
        # similarities.append(followers_sim)
        # consumption_followers_sim = jaccard_similarity(top_consumption, top_followers)
        # similarities.append(consumption_followers_sim)
        similarities.append(jaccard_similarity(top_production, top_rel_production))
        similarities.append(jaccard_similarity(top_rel_production, top_consumption))
        similarities.append(jaccard_similarity(top_rel_production, top_followers))
        log.info(similarities)
        title = "Similarity of Top " + str(5*i) + " Users of Utility Functions for " \
                                                  "Cluster " + str(cluster_num) + " at Local Threshold " + str(thresh)
        #plt.bar(['Consumption and Production', 'Local Followers and Production', 'Consumption and Local Followers' ], similarities)
        plt.bar(['Relative Production and Production', 'Relative Production and Consumption',
                 'Relative Production and Local Followers'], similarities)
        plt.ylabel('Jaccard Similarity')
        plt.xlabel('Utility Function')
        plt.title(title)
        plt.show()

        # top_consumption_names = [user.screen_name for user in user_getter.get_users_by_id_list(top_consumption)]
        # log.info(top_consumption_names)
        top_production_names = [user.screen_name for user in user_getter.get_users_by_id_list(top_production)]
        log.info(top_production_names)
        # top_followers_names = [user.screen_name for user in user_getter.get_users_by_id_list(top_followers)]
        # log.info(top_followers_names)
        top_rel_production_names = [user.screen_name for user in user_getter.get_users_by_id_list(top_rel_production)]
        log.info(top_rel_production_names)

def compare_across_time(user_name, thresh):
    for i in range(1, 4):
        similarities = []
        con_file = ("./dc2_exp/consumptionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
        con_restricted_file = ("./dc2_exp/consumptiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
        prod_file = ("./dc2_exp/productionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
        prod_restricted_file = ("./dc2_exp/productiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
        with open(con_file, 'r') as file:
            con = json.load(file)
        with open(con_restricted_file, 'r') as file:
            con_restricted = json.load(file)
        with open(prod_file, 'r') as file:
            prod = json.load(file)
        with open(prod_restricted_file, 'r') as file:
            prod_restricted = json.load(file)
        con_sim = jaccard_similarity(con[:20], con_restricted[:20])
        similarities.append(con_sim)
        prod_sim = jaccard_similarity(prod[:20], prod_restricted[:20])
        similarities.append(prod_sim)

        title = "Similarity of Top 20 Users of Utility Functions for " \
                                                  "Cluster " + str(i) + " at Local Threshold " + str(thresh) + " with Time Restricted Tweets"
        plt.bar(['Consumption', 'Production'], similarities)
        plt.ylabel('Jaccard Similarity')
        plt.xlabel('Utility Function')
        plt.title(title)
        plt.show()


def similarity_matrix(user_name, thresh, i, first: str, second: str, friends_getter, cluster):
    con_file = ("./dc2_exp/consumptionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    con_restricted_file = ("./dc2_exp/consumptiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    prod_file = ("./dc2_exp/productionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    prod_restricted_file = ("./dc2_exp/productiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    with open(con_file, 'r') as file:
        con = json.load(file)
    with open(con_restricted_file, 'r') as file:
        con_restricted = json.load(file)
    with open(prod_file, 'r') as file:
        prod = json.load(file)
    with open(prod_restricted_file, 'r') as file:
        prod_restricted = json.load(file)
    top25_con = con_restricted[:25]
    top25_prod = prod_restricted[:25]
    intersect = set(top25_prod).intersection(top25_con)
    remaining_con = set(top25_con) - intersect
    remaining_prod = set(top25_prod) - intersect

    if first == 'a':
        set1 = intersect
    if first == 'p':
        set1 = remaining_prod
    if first == 'c':
        set1 = remaining_con
    if second == 'a':
        set2 = intersect
    if second == 'p':
        set2 = remaining_prod
    if second == 'c':
        set2 = remaining_con

    print("A_c: ", remaining_con)
    print("A_p: ", remaining_prod)
    print("A: ", intersect)
    local_friends = {}
    for user in (intersect | remaining_con | remaining_prod):
        friends = [str(id) for id in friends_getter.get_user_friends_ids(user)]
        local_friends[user] = set(friends).intersection(cluster)

    print("\nRows: A_p, Columns: A_p")
    make_matrix(remaining_prod, remaining_prod, local_friends)
    print("\nRows: A_c, Columns: A_c")
    make_matrix(remaining_con, remaining_con, local_friends)
    print("\nRows: A_p, Columns: A_c")
    make_matrix(remaining_prod, remaining_con, local_friends)
    print("\nRows: A, Columns: A")
    make_matrix(intersect, intersect, local_friends)
    print("\nRows: A, Columns: A_c")
    make_matrix(intersect, remaining_con, local_friends)
    print("\n Rows: A, Columns: A_p")
    make_matrix(intersect, remaining_prod, local_friends)

def similarity_retweets_matrix(user_name, thresh, i, tweet_getter, cluster):
    con_file = ("./dc2_exp/consumptionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    con_restricted_file = ("./dc2_exp/consumptiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    prod_file = ("./dc2_exp/productionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    prod_restricted_file = ("./dc2_exp/productiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    with open(con_file, 'r') as file:
        con = json.load(file)
    with open(con_restricted_file, 'r') as file:
        con_restricted = json.load(file)
    with open(prod_file, 'r') as file:
        prod = json.load(file)
    with open(prod_restricted_file, 'r') as file:
        prod_restricted = json.load(file)
    top25_con = con_restricted[:25]
    top25_prod = prod_restricted[:25]
    intersect = set(top25_prod).intersection(top25_con)
    remaining_con = set(top25_con) - intersect
    remaining_prod = set(top25_prod) - intersect

    print("A_c: ", remaining_con)
    print("A_p: ", remaining_prod)
    print("A: ", intersect)
    local_retweets = {}
    users = (intersect | remaining_con | remaining_prod)
    for user in users:
        retweets = tweet_getter.get_retweets_by_user_id_time_restricted(user)
        tweets = []
        for retweet in retweets:
            original_id = retweet.retweet_id
            if str(retweet.retweet_user_id) in cluster:
                tweets.append(original_id)

        local_retweets[user] = tweets

    print("\nRows: A_p, Columns: A_p")
    make_matrix(remaining_prod, remaining_prod, local_retweets)
    print("\nRows: A_c, Columns: A_c")
    make_matrix(remaining_con, remaining_con, local_retweets)
    print("\nRows: A_p, Columns: A_c")
    make_matrix(remaining_prod, remaining_con, local_retweets)
    print("\nRows: A, Columns: A")
    make_matrix(intersect, intersect, local_retweets)
    print("\nRows: A, Columns: A_c")
    make_matrix(intersect, remaining_con, local_retweets)
    print("\n Rows: A, Columns: A_p")
    make_matrix(intersect, remaining_prod, local_retweets)

def make_matrix(set1, set2, local_friends):
    array = []
    for user1 in set1:
        row = []
        for user2 in set2:
            row.append(round(jaccard_similarity(local_friends[user1], local_friends[user2]), 2))
        array.append(row)

    np.set_printoptions(linewidth=130)
    print(np.array(array))

def similarity_graph(user_name, seed_id, thresh, i, friends_getter, cluster, clusterer):
    con_file = ("./dc2_exp/consumptionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    con_restricted_file = ("./dc2_exp/consumptiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    prod_file = ("./dc2_exp/productionrankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    prod_restricted_file = ("./dc2_exp/productiontime_restricted_rankings" + "/local_" + str(thresh) + "_global_50" + str("/") + user_name + '_all_cluster_' + str(i) + '.json')
    with open(con_file, 'r') as file:
        con = json.load(file)
    with open(con_restricted_file, 'r') as file:
        con_restricted = json.load(file)
    with open(prod_file, 'r') as file:
        prod = json.load(file)
    with open(prod_restricted_file, 'r') as file:
        prod_restricted = json.load(file)
    top25_con = con_restricted[:25]
    top25_prod = prod_restricted[:25]
    intersect = set(top25_prod).intersection(top25_con)
    remaining_con = set(top25_con) - intersect
    remaining_prod = set(top25_prod) - intersect

    local_friends = {}
    for user in (intersect | remaining_con | remaining_prod):
        friends = [str(id) for id in friends_getter.get_user_friends_ids(user)]
        local_friends[user] = set(friends).intersection(cluster)

    users = intersect | remaining_con | remaining_prod
    graph = get_graph(users, local_friends)
    clusters = clusterer.cluster_by_graph(seed_id, graph)


def get_graph(users, local_friends) -> nx.Graph:
    graph = nx.Graph()

    for agent in users:
        graph.add_node(agent)

    # Edges between user1 and user2 indicate that both users local following
    # sets that have Jaccard similarity >= 0.1

    for user1 in users:
        for user2 in users:
            lst1 = local_friends[user1]
            lst2 = local_friends[user2]
            if jaccard_similarity(lst1, lst2) >= 0.1 and user1 != user2:
                graph.add_edge(user1, user2)

    return graph

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


def jaccard_similarity(user_list1, user_list2):
    intersection = len(list(set(user_list1).intersection(user_list2)))
    union = (len(user_list1) + len(user_list2)) - intersection
    if intersection == 0:
        return 0
    return float(intersection) / union

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

    args = parser.parse_args()
    ranking_distribution(args.name, args.thresh)
    #compare_across_time(args.name, args.thresh)
