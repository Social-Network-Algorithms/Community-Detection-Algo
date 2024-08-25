import math

import src.dependencies.injector as sdi
from src.shared.utils import get_project_root, jaccard_similarity
from src.shared.logger_factory import LoggerFactory
from src.model.local_neighbourhood import LocalNeighbourhood
from typing import List
from src.model.user import User
from src.model.social_graph.social_graph import SocialGraph
from src.model.cluster import Cluster



log = LoggerFactory.logger(__name__)
DEFAULT_PATH = str(get_project_root()) + \
               "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def create_social_graph(screen_name: str, user_activity: str, path=DEFAULT_PATH) -> tuple:
    """Returns a social graph and the local neighbourhood of the user with screen_name constructed
    out of the data in the local mongodb database.
    """
    try:
        log.info(f"Creating a Social Graph, with activity={user_activity}:")
        injector = sdi.Injector.get_injector_from_file(path)
        process_module = injector.get_process_module()
        dao_module = injector.get_dao_module()

        user = get_user_by_screen_name(screen_name, path)
        local_neighbourhood_getter = dao_module.get_local_neighbourhood_getter(user_activity)
        local_neighbourhood = local_neighbourhood_getter.get_local_neighbourhood(
            user.id)
        if local_neighbourhood is None:
            # Download the local neighbourhood if it doesn't exist
            log.info(
                f"Downloading local neighbourhood for {user.screen_name} {user.id}")
            local_neighbourhood_downloader = process_module.get_local_neighbourhood_downloader(user_activity)
            local_neighbourhood_downloader.download_local_neighbourhood_by_id(
                user.id)
            local_neighbourhood = local_neighbourhood_getter.get_local_neighbourhood(user.id)

        social_graph_constructor = process_module.get_social_graph_constructor(user_activity)
        social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(
            local_neighbourhood)
        return social_graph, local_neighbourhood

    except Exception as e:
        log.exception(e)
        log.exception(f'{user.screen_name} {user.id} {type(user.id)}')
        exit()


def create_social_graph_from_local_neighbourhood(local_neighbourhood: LocalNeighbourhood,
                                                 user_activity: str,
                                                 path=DEFAULT_PATH):
    """Returns a social graph of the local neighbourhood."""
    try:
        injector = sdi.Injector.get_injector_from_file(path)
        process_module = injector.get_process_module()

        social_graph_constructor = process_module.get_social_graph_constructor(user_activity)
        social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(
            local_neighbourhood)
        return social_graph

    except Exception as e:
        log.exception(e)
        exit()


def calculate_threshold(local_neighbourhood, top_num, thresh_multiplier):
    user_list = local_neighbourhood.get_user_id_list()
    jaccard_sim = []
    for user_1 in user_list:
        activities = local_neighbourhood.get_user_activities(user_1)
        for user_2 in user_list:
            if user_1 != user_2:
                sim = jaccard_similarity(
                    activities, local_neighbourhood.get_user_activities(user_2))
                jaccard_sim.append(sim)

    jaccard_sim.sort(reverse=True)
    # graph_list(jaccard_sim, "Pairs of Users",
    #            "Jaccard Similarity", "all_jac_sim_users.png")
    # graph_list(jaccard_sim[:100], "Pairs of Users",
    #            "Jaccard Similarity", "top_jac_sim_users.png")
    if len(jaccard_sim) >= top_num:
        threshold = sum(jaccard_sim[:top_num]) / \
                    top_num * thresh_multiplier
    elif len(jaccard_sim) == 0:
        threshold = 0
    else:
        threshold = sum(jaccard_sim[:len(jaccard_sim)]) / \
                    len(jaccard_sim) * thresh_multiplier
    # print(threshold)
    if threshold >= 0.001:
        threshold = math.floor(threshold * 1000) / 1000
    print('chosen threshold', threshold)
    return threshold


def refine_social_graph_jaccard_users(user_id: str, social_graph: SocialGraph,
                                      local_neighbourhood: LocalNeighbourhood, user_activity: str,
                                      top_num: int = 50,
                                      thresh_multiplier: float = 0.1, threshold: float = -1.0,
                                      sample_prop: float = 1,
                                      weighted: bool = True,
                                      path=DEFAULT_PATH) -> SocialGraph:
    """Returns a social graph refined using Jaccard Set Similarity using the social graph and the screen name of the user."""
    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()

    user_list = local_neighbourhood.get_user_id_list()

    if threshold == -1.0:
        threshold = calculate_threshold(local_neighbourhood, top_num, thresh_multiplier)

    log.info("Refining by Jaccard Similarity:")

    MIN_RETWEETS = 3
    MAX_USERS_RETWEETED = 100

    users_map = {}
    weights_map = {}
    user_to_activity = {}

    for user_1 in user_list:
        activities1 = local_neighbourhood.get_user_activities(user_1, sample_prop)
        if user_activity == "user retweets":
            # Filters out retweeted users with less than MIN_RETWEETS retweets
            activities1 = _find_k_repeats(activities1, MIN_RETWEETS)
            # If too large, we may try higher min_retweets
            i = 0
            while len(set(activities1)) > MAX_USERS_RETWEETED:  # note that we first remove duplicates
                i += 1
                activities1 = _find_k_repeats(activities1, MIN_RETWEETS + i)
        user_to_activity[user_1] = activities1

    for user_1 in user_list:
        activities1 = user_to_activity[user_1]
        users_map[user_1] = []
        weights_map[user_1] = {}
        for user_2 in user_list:
            if user_1 != user_2:
                activities2 = user_to_activity[user_2]
                sim = jaccard_similarity(
                    activities1, activities2)
                if sim >= threshold:
                    users_map[user_1].append(user_2)
                    weights_map[user_1][user_2] = sim

    log.info("Setting Local Neighbourhood:")
    refined_local_neighbourhood = LocalNeighbourhood(
        str(user_id), None, users_map)
    social_graph_constructor = process_module.get_social_graph_constructor(user_activity)

    refined_social_graph = social_graph_constructor.construct_weighted_social_graph_from_local_neighbourhood(
        refined_local_neighbourhood, weights_map) if weighted else \
        social_graph_constructor.construct_social_graph_from_local_neighbourhood(
            refined_local_neighbourhood)

    return refined_social_graph


def clustering_from_social_graph(screen_name: str, social_graph: SocialGraph, path=DEFAULT_PATH) -> List[Cluster]:
    """Returns clusters from the social graph and screen name of user."""
    try:
        log.info("Clustering:")
        user = get_user_by_screen_name(screen_name, path)
        injector = sdi.Injector.get_injector_from_file(path)
        process_module = injector.get_process_module()
        dao_module = injector.get_dao_module()
        clusterer = process_module.get_clusterer()
        
        # Return nothing if social graph too small
        if len(social_graph.graph.nodes) < 5:
            return []
        clusters = clusterer.cluster_by_social_graph(
            user.id, social_graph, None)
        return clusters
    except Exception as e:
        log.exception(e)
        exit()


def get_user_by_screen_name(screen_name: str, path=DEFAULT_PATH) -> User:
    """Returns a user object from their bluesky screen name."""
    injector = sdi.Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    user_getter = dao_module.get_user_getter()
    user = user_getter.get_user_by_screen_name(screen_name)
    return user


###################################################
def update_size_count_dict(size_count_dict, clusters):
    for cluster in clusters:
        size = len(cluster.users)
        if size not in size_count_dict:
            size_count_dict[size] = 1
        else:
            size_count_dict[size] += 1
    print(size_count_dict)
    return size_count_dict

def _find_k_repeats(lst, k):
    """Filters out elements that appear less than k times in lst."""
    return [x for x in lst if lst.count(x) >= k]


def compute_expected_cluster_size(cluster_lst: List[Cluster]) -> float:
    """
    Return the expected size of clusters given the list of clusters <cluster_lst>.
    """
    size_count_dict = update_size_count_dict({}, cluster_lst)

    total_count = sum(size_count_dict.values())
    expected_size = 0

    for size in size_count_dict:
        expected_size += size * size_count_dict[size] / total_count

    return expected_size


def filter_by_expected_size(cluster_lst: List[Cluster]) -> List[Cluster]:
    """
    cluster_lst: list of clusters to filter

    Compute the expected size for a single cluster of cluster_lst

    Next, filter out the clusters whose size is below the expected size, and return the remaining
    clusters as a list"""

    expected_size = compute_expected_cluster_size(cluster_lst)
    print(f"expected size is {expected_size}")

    filtered_clusters = []
    for cluster in cluster_lst:
        if len(cluster.users) >= 10:
            filtered_clusters.append(cluster)

    return filtered_clusters
