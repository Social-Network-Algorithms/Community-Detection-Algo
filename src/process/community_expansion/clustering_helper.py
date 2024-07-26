import networkx as nx
import igraph as ig
import src.dependencies.injector as sdi
from src.clustering_experiments.create_social_graph_and_cluster import _find_k_repeats
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker
from src.shared.utils import get_project_root

path = str(get_project_root()) + \
       "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
injector = sdi.Injector.get_injector_from_file(path)
process_module = injector.get_process_module()
dao_module = injector.get_dao_module()
friends_getter = dao_module.get_user_friend_getter()
retweeted_users_getter = dao_module.get_retweeted_users_getter()


def construct_social_graph(candidates, thresh):
    """
    Construct the social graph for the filtered candidates from round 2 to do clustering on.
    """
    MIN_RETWEETS = 3
    MAX_USERS_RETWEETED = 200
    users_map = {}
    weights_map = {}
    user_to_activity = {}

    for user_1 in candidates:
        activities1 = retweeted_users_getter.get_retweet_users_ids(user_1)
        # Filters out retweeted users with less than MIN_RETWEETS retweets
        activities1 = _find_k_repeats(activities1, MIN_RETWEETS)
        # If too large, we may try higher min_retweets
        i = 0
        while len(set(activities1)) > MAX_USERS_RETWEETED:  # note that we first remove duplicates
            i += 1
            activities1 = _find_k_repeats(activities1, MIN_RETWEETS + i)
        user_to_activity[user_1] = activities1

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

    graph = nx.DiGraph()
    for user in candidates:
        friends = users_map[user]
        for friend in friends:
            graph.add_edge(user, friend, weight=weights_map[user][friend])

    return graph


def cluster_social_graph_helper(soc_graph, top_size):
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
    for cluster in clusters_data:
        if len(cluster) >= top_size:
            refined_clusters.append(cluster)

    return refined_clusters


def cluster_social_graph(soc_graph, thresh, end_thresh, increment, top_size):
    """
    Cluster the social graph for the filtered candidates.
    """
    all_clusters = []
    if thresh > end_thresh:
        return all_clusters

    clusters = cluster_social_graph_helper(soc_graph, top_size)
    all_clusters.extend(clusters)
    thresh += increment
    for cluster in clusters:
        new_soc_graph = construct_social_graph(cluster, thresh)
        child_clusters = cluster_social_graph(new_soc_graph, thresh, end_thresh, increment, top_size)
        if len(child_clusters) > 1:
            all_clusters.extend(child_clusters)

    return all_clusters


def select_cluster(clusters, current_community, sosu_ranker: CommunitySocialSupportRanker, top_size):
    cluster_scores = []

    for j in range(len(clusters)):
        cluster = clusters[j]
        # social support
        sosu_ranker_scores = sosu_ranker.score_users(cluster, cluster)
        sosu_ranking = list(
            sorted(sosu_ranker_scores, key=lambda x: (sosu_ranker_scores[x]),
                   reverse=True))
        top_10 = sosu_ranking[:top_size]
        cluster_score = sum(sosu_ranker.score_users(current_community, top_10).values())

        cluster_scores.append(cluster_score)
    print('cluster scores: ', cluster_scores)
    if len(cluster_scores) > 0:
        max_score_index = cluster_scores.index(max(cluster_scores))
        return clusters[max_score_index]
    else:
        return []


def jaccard_similarity(user_list1, user_list2):
    intersection = len(set(user_list1).intersection(set(user_list2)))
    union = (len(user_list1) + len(user_list2)) - intersection
    if union == 0:
        return 0
    return float(intersection) / union
