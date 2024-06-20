import src.dependencies.injector as sdi
from src.clustering_experiments import ranking_users_in_clusters as rank
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
from src.process.data_cleaning.data_cleaning_distributions import jaccard_similarity
from src.model.local_neighbourhood import LocalNeighbourhood
# Just for type signatures
from typing import List
from src.model.user import User
from src.model.social_graph.social_graph import SocialGraph
from src.model.cluster import Cluster
import matplotlib.pyplot as plt
# import ranking_users_in_clusters as rank


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


def refine_social_graph_jaccard(screen_name: str, social_graph: SocialGraph,
                                local_neighbourhood: LocalNeighbourhood, user_activity: str, top_num: int = 10,
                                thresh_multiplier: float = 0.1, threshold: float = -1.0,
                                sample_prop: float = 1,
                                path=DEFAULT_PATH) -> SocialGraph:
    """Returns a social graph refined using Jaccard Set Similarity using the social graph and the screen name of the user."""
    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()
    user_friend_getter = dao_module.get_user_friend_getter()

    user_id = get_user_by_screen_name(screen_name).id
    user_list = local_neighbourhood.get_user_id_list()
    jaccard_sim = []

    """
    Code structure:
    Note how this both adds and removes edges: if there was an edge b/w user1 and user2
    however, their sim is too low, then the edge is removed. If there was no edge b/w
    user1 and user2, but their sim is high enough, then an edge is added.

    for user1 in user_list:
        activities = local_neighbourhood.get_user_activities(user1)
        for user2 in user_list:
            if user1 != user2:
                sim = jaccard_similarity(activities, local_neighbourhood.get_user_activities(user2))
                if sim >= threshold:
                    jaccard_sim.append(sim)
    """

    def calculate_threshold():
        for user1 in user_list:
            activities = local_neighbourhood.get_user_activities(user1)
            for user2 in user_list:
                if user1 != user2:
                    sim = jaccard_similarity(activities, local_neighbourhood.get_user_activities(user2))
                    if sim >= threshold:
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
        return threshold

    if threshold == -1.0:
        threshold = calculate_threshold()

    log.info("Refining by Jaccard Similarity:")
    friends_map = {}
    for user1 in user_list:
        activities = local_neighbourhood.get_user_activities(user1, sample_prop)
        friends_map[user1] = []
        for user2 in user_list:
            if user1 != user2:
                sim = jaccard_similarity(
                    activities, local_neighbourhood.get_user_activities(user2, sample_prop))
                if sim >= threshold:
                    friends_map[user1].append(user2)

    log.info("Setting Local Neighbourhood:")
    refined_local_neighbourhood = LocalNeighbourhood(
        str(user_id), None, friends_map)
    social_graph_constructor = process_module.get_social_graph_constructor(user_activity)
    refined_social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(
        refined_local_neighbourhood)

    return refined_social_graph


def refine_social_graph_jaccard_users(screen_name: str, social_graph: SocialGraph,
                                      local_neighbourhood: LocalNeighbourhood, user_activity: str,
                                      top_num: int = 10,
                                      thresh_multiplier: float = 0.1, threshold: float = -1.0,
                                      sample_prop: float = 1,
                                      weighted: bool = True,
                                      path=DEFAULT_PATH) -> SocialGraph:
    """Returns a social graph refined using Jaccard Set Similarity using the social graph and the screen name of the user."""
    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()
    user_friend_getter = dao_module.get_user_friend_getter()

    if not screen_name.isnumeric():
        user_id = get_user_by_screen_name(screen_name).id
    else:
        user_id = screen_name
    user_list = local_neighbourhood.get_user_id_list()
    jaccard_sim = []

    def calculate_threshold():
        for user_1 in user_list:
            activities = local_neighbourhood.get_user_activities(user_1)
            for user_2 in user_list:
                if user_1 != user_2:
                    sim = jaccard_similarity(
                        activities, local_neighbourhood.get_user_activities((user_2)))
                    jaccard_sim.append(sim)

        jaccard_sim.sort(reverse=True)
        graph_list(jaccard_sim, "Pairs of Users",
                   "Jaccard Similarity", "all_jac_sim_users.png")
        graph_list(jaccard_sim[:100], "Pairs of Users",
                   "Jaccard Similarity", "top_jac_sim_users.png")
        if len(jaccard_sim) >= top_num:
            threshold = sum(jaccard_sim[:top_num]) / \
                top_num * thresh_multiplier
        elif len(jaccard_sim) == 0:
            threshold = 0
        else:
            threshold = sum(jaccard_sim[:len(jaccard_sim)]) / \
                len(jaccard_sim) * thresh_multiplier
        return threshold

    if threshold == -1.0:
        threshold = calculate_threshold()

    log.info("Refining by Jaccard Similarity:")

    MIN_RETWEETS = 3  # TODO: decide
    MAX_USERS_RETWEETED = 300 # TODO: decide

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
        while len(set(activities1)) > MAX_USERS_RETWEETED: # note that we first remove duplicates
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


def refine_social_graph_jaccard_with_friends(screen_name: str, social_graph: SocialGraph,
                                             local_neighbourhood: LocalNeighbourhood, user_activity: str, threshold=0.5,
                                             sample_prop: float = 1,
                                             path=DEFAULT_PATH) -> SocialGraph:
    """Returns a social graph refined using Jaccard Set Similarity using the social graph and the screen name of the user."""
    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()
    user_friend_getter = dao_module.get_user_friend_getter()
    if not screen_name.isnumeric():
        user_id = get_user_by_screen_name(screen_name).id
    else:
        user_id = screen_name
    user_list = local_neighbourhood.get_user_id_list()
    jaccard_sim = []

    graph_user_following(user_list, local_neighbourhood)
    for user1 in user_list:
        activities = local_neighbourhood.get_user_activities(user1)
        for user2 in user_list:
            if user1 != user2:
                sim = jaccard_similarity(activities, local_neighbourhood.get_user_activities(user2))
                jaccard_sim.append(sim)

    jaccard_sim.sort(reverse=True)
    graph_list(jaccard_sim, "Pairs of Users",
               "Jaccard Similarity", "all_jac_sim.png")
    graph_list(jaccard_sim[:100], "Pairs of Users",
               "Jaccard Similarity", "top_jac_sim.png")

    log.info("Refining by Jaccard Similarity:")
    friends_map = {}
    for user1 in user_list:
        activities = local_neighbourhood.get_user_activities(user1, sample_prop)
        friends_map[user1] = []
        for user2 in user_list:
            if user1 != user2:
                sim = jaccard_similarity(
                    activities, local_neighbourhood.get_user_activities(user2, sample_prop))
                if sim >= threshold:
                    friends_map[user1].append(user2)

    log.info("Setting Local Neighbourhood:")
    refined_local_neighbourhood = LocalNeighbourhood(
        str(user_id), None, friends_map)
    social_graph_constructor = process_module.get_social_graph_constructor(user_activity)
    refined_social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(
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
    """Returns a user object from their twitter screen name."""
    injector = sdi.Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    user_getter = dao_module.get_user_getter()
    user = user_getter.get_user_by_screen_name(screen_name)
    return user


def graph_user_following(user_list, local_neighbourhood):
    activities_list_val = []
    for user in user_list:
        if user == '359831209':
            continue
        activities = local_neighbourhood.get_user_activities(user)
        activities_list_val.append(len(activities))
    activities_list_val.sort(reverse=True)
    graph_list(activities_list_val, "Users",
               "Number of activities", "all_following.png")
    graph_list(activities_list_val[:10], "Users",
               "number of activities", "top_following.png")


def graph_list(y_val, x_label, y_label, fig_name):
    plt.figure()
    plt.plot(y_val)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(fig_name)


def discard_small_clusters(clusters):
    """Returns the number of large clusters in the list of clusters sorted in descending order of size.
    This works by finding an adaptive cut-off discard size above which all clusters are
    said to be "large" clusters.
    """
    total_users = sum(len(c.users) for c in clusters)
    # Remove clusters of size < 2% of the total number of users
    too_small = 0.02 * total_users
    updated_clusters = []
    for i in range(len(clusters)):
        if len(clusters[i].users) < too_small:
            pass
        else:
            updated_clusters.append(clusters[i])

    gaps = []
    for i in range(1, len(updated_clusters)):
        gap = len(updated_clusters[i - 1].users) - \
            len(updated_clusters[i].users)
        # i is the number of updated_clusters larger than a
        # cut-off discard size chosen at the gap.
        gaps.append((i, gap))
    # Final gap is gap from 0 to the smallest cluster
    final_gap = len(updated_clusters[len(updated_clusters) - 1].users) - 0
    gaps.append((len(updated_clusters), final_gap))

    gaps.sort(key=lambda g: g[1], reverse=True)

    wide_range = set(range(1, 9))
    viable_range = set(range(3, 6))

    # Initialize them to 0
    outside_wide_num = 0
    wide_num = 0
    for j in range(min(3, len(gaps))):
        num_clusters = gaps[j][0]
        if num_clusters in viable_range:
            return num_clusters
        elif num_clusters in wide_range and wide_num in (0, 1):
            wide_num = num_clusters
        elif num_clusters not in wide_range and outside_wide_num == 0:
            outside_wide_num = num_clusters
    if wide_num != 0:
        return wide_num
    return outside_wide_num


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


def graph_cluster_size(cluster_set, threshold, user):
    size_count_dict = update_size_count_dict({}, cluster_set)

    # Also consider the case where size_count_dict is empty:
    if len(size_count_dict.keys()) == 0:
        upper_bound = 0
    else:
        upper_bound = max(size_count_dict.keys())

    # x-axis is size, y-axis is number of clusters
    fig, ax = plt.subplots()

    count_list = []
    key_str_list = []

    for i in range(upper_bound + 1):
        key_str_list.append(str(i))
        if i not in size_count_dict:
            count_list.append(0)
        else:
            count_list.append(size_count_dict[i])

    ax.bar(key_str_list, count_list)

    ax.set_title(
        f'Number of Clusters for Each Size, threshold={threshold} -- {user}')
    ax.set_ylabel(f'Count of Cluster given Size')
    ax.set_xlabel('Size of clusters')

    # disable the overlapping labels on the x
    plt.xticks([])

    plt.show()


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

    # size_count_dict = update_size_count_dict({}, cluster_lst)
    #
    # total_count = sum(size_count_dict.values())
    # expected_size = 0
    #
    # for size in size_count_dict:
    #     expected_size += size * size_count_dict[size] / total_count

    expected_size = compute_expected_cluster_size(cluster_lst)
    print(f"expected size is {expected_size}")

    filtered_clusters = []
    for cluster in cluster_lst:
        # Size threshold between 10 and 20
        # TODO: decide on the size threshold to filter out small clusters
        if len(cluster.users) >= 10:
            filtered_clusters.append(cluster)

    return filtered_clusters


if __name__ == "__main__":

    thresh = 0.4
    top = []
    # timnitGebru
    # Play around with threshold multiplier and top num
    social_graph, local_neighbourhood = create_social_graph("fchollet")

    # refined_social_graph = refine_social_graph_jaccard_with_friends("timnitGebru", social_graph, local_neighbourhood, threshold=0.2)
    refined_social_graph = refine_social_graph_jaccard_users("fchollet", social_graph, local_neighbourhood,
                                                             threshold=thresh)
    clusters = clustering_from_social_graph("fchollet", refined_social_graph)
    clusters_filtered_by_size = filter_by_expected_size(clusters)
    path = DEFAULT_PATH
    # refined_clusters = clustering_from_social_graph("mikarv", refined_social_graph)
    for cluster in clusters_filtered_by_size:
        print("Users in the clusters:")
        injector = sdi.Injector.get_injector_from_file(path)
        dao_module = injector.get_dao_module()
        user_getter = dao_module.get_user_getter()
        base_user = user_getter.get_user_by_id(cluster.base_user)
        users = []
        for user in cluster.users:
            users.append(user_getter.get_user_by_id(user).screen_name)
        users.sort()
        print(users)
        top_10 = rank.rank_users("fchollet", cluster)
        top.append(top_10)
    # Compare the clusters before & after   filtering
    # graph_cluster_size(clusters, thresh, "fchollet")
    # graph_cluster_size(clusters_filtered_by_size, thresh, "fchollet")
    print(top)
