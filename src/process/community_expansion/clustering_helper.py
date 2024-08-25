from typing import List

import networkx as nx
import igraph as ig
from src.clustering_experiments.build_cluster_tree import visualize_forest1, trace_no_redundant_nodes, \
    package_cluster_nodes
from src.model.cluster import Cluster
from src.model.cluster_tree import ClusterNode
from src.shared.utils import jaccard_similarity


def calculate_threshold_friends(friends_getter, user_list, top_num, thresh_multiplier):
    """Calculate the threshold used for Jaccard similarity when clustering the local neighborhood"""
    jaccard_sim = []
    for user_1 in user_list:
        activities = friends_getter.get_user_friends_ids(user_1)
        for user_2 in user_list:
            if user_1 != user_2:
                sim = jaccard_similarity(
                    activities, friends_getter.get_user_friends_ids(user_2))
                jaccard_sim.append(sim)

    jaccard_sim.sort(reverse=True)

    if len(jaccard_sim) >= top_num:
        threshold = sum(jaccard_sim[:top_num]) / \
                    top_num * thresh_multiplier
    elif len(jaccard_sim) == 0:
        threshold = 0
    else:
        threshold = sum(jaccard_sim[:len(jaccard_sim)]) / \
                    len(jaccard_sim) * thresh_multiplier

    print('chosen threshold for social graph refinement', threshold)
    return threshold


def construct_social_graph_friends(friends_getter, candidates, thresh):
    """
    Construct the social graph for the filtered candidates from round 2 to do clustering on
    (based on friends user activity).
    """
    users_map = {}
    weights_map = {}
    user_to_activity = {}

    for user in candidates:
        activities1 = friends_getter.get_user_friends_ids(user)
        user_to_activity[user] = activities1

    for user_1 in candidates:
        activities1 = user_to_activity[user_1]
        users_map[user_1] = []
        weights_map[user_1] = {}
        for user_2 in candidates:
            if user_1 != user_2:
                activities2 = user_to_activity[user_2]
                sim = jaccard_similarity(
                    activities1, activities2)
                if sim >= thresh:
                    users_map[user_1].append(user_2)
                    weights_map[user_1][user_2] = sim

    connected_users = remove_unconnected_nodes(users_map)
    # print("Number of unconnected nodes removed ", len(candidates) - len(connected_users))

    graph = nx.DiGraph()
    for user in connected_users:
        friends = users_map[user]
        for friend in friends:
            graph.add_edge(user, friend, weight=weights_map[user][friend])

    return graph


def cluster_social_graph(friends_getter, soc_graph,
                         thresh: float, end_thresh: float, increment: float,
                         level_one: bool = False) -> List[ClusterNode]:
    if thresh > end_thresh:
        return []

    # generate the clusters
    clusters = cluster_social_graph_helper(soc_graph, level_one=level_one)

    # Set ranked=True when visualizing tree
    parent_nodes = package_cluster_nodes("", clusters, thresh, ranked=False)
    thresh += increment
    for parent_node in parent_nodes:
        new_soc_graph = construct_social_graph_friends(friends_getter, parent_node.root.users, thresh)
        child_nodes = cluster_social_graph(friends_getter, new_soc_graph, thresh, end_thresh, increment,
                                           level_one=False)
        for child_node in child_nodes:
            child_node.parent = parent_node
            parent_node.children.append(child_node)
    return parent_nodes


def cluster_social_graph_helper(soc_graph, level_one=False) -> List[Cluster]:
    if len(soc_graph.nodes) < 5:
        return []

    clusters_data = []
    if soc_graph.number_of_nodes() > 0:
        graph = ig.Graph.from_networkx(soc_graph)  # make igraph from networkx graph
        graph.vs["name"] = graph.vs["_nx_name"]
        clustering = ig.Graph.community_walktrap(graph, graph.es['weight'], 4).as_clustering()
        for cluster in clustering:
            cluster_list_ids = []
            for node_id in cluster:
                cluster_list_ids.append(graph.vs[node_id]["name"])
            clusters_data.append(cluster_list_ids)

    refined_clusters = []
    for cluster_data in clusters_data:
        if len(cluster_data) >= 10:
            cluster = Cluster("", cluster_data)
            refined_clusters.append(cluster)

    if level_one and len(refined_clusters) == 0:
        for cluster_data in clusters_data:
            cluster = Cluster("", cluster_data)
            refined_clusters.append(cluster)

    return refined_clusters


def get_all_clusters(main_roots):
    # i = random()
    # print(i)
    # visualize_forest1("", main_roots, i)
    no_redundant_nodes = trace_no_redundant_nodes(main_roots)
    clusters = []

    for n in no_redundant_nodes:
        clusters.append(n.root.users)
    return clusters


def select_cluster(clusters, core_users):
    """Select the cluster with the highest number of overlaps with the core users"""
    cluster_scores = []

    for j in range(len(clusters)):
        cluster = clusters[j]
        cluster_score = len(set(cluster).intersection(core_users))
        cluster_scores.append(cluster_score)
    print('cluster scores: ', cluster_scores)
    if len(cluster_scores) > 0:
        max_score_index = cluster_scores.index(max(cluster_scores))
        return clusters[max_score_index]
    else:
        return []


def remove_unconnected_nodes(user_dict):
    count = 1
    while count > 0:
        count = 0
        keys = list(user_dict.keys())
        for user in keys:
            if len(user_dict[user]) == 0:
                count += 1
                del user_dict[user]
                for key in user_dict.keys():
                    if user in user_dict[key]:
                        user_dict[key].remove(user)

    user_list = list(user_dict.keys())

    return user_list
