from src.clustering_experiments import create_social_graph_and_cluster as csgc
from src.model.cluster import Cluster
from src.model.cluster_tree import ClusterNode

from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
from src.model.local_neighbourhood import LocalNeighbourhood
from typing import List, Optional
from src.clustering_experiments import ranking_users_in_clusters as rank
import src.dependencies.injector as sdi
import pygraphviz as pgv
import os

log = LoggerFactory.logger(__name__)
DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

from src.process.data_cleaning.data_cleaning_distributions import jaccard_similarity


def _find_top_users(core_detector, cluster: Cluster, top_num: int) -> List[str]:
    """
    Use <core_detector> to find (by production utility), the top <top_num> users in <cluster> with the highest
    scores, return a list of user ids of these users.
    """
    scores = core_detector.prod_ranker.score_users(cluster.users)
    top_users = [k for k, v in sorted(scores.items(), key=lambda item: item[1])][:top_num]

    return top_users


def construct_edges_by_topuser(core_detector,
                               parents: List[ClusterNode],
                               children: List[ClusterNode],
                               top_num=10):
    """
    - Modify parents and children (2 lists of tree nodes) by establishing edges between them.
    - Edge is established between a parent and a child iff, the parent has the highest similarity of top users
      with the child among all parents.
    - top_num is the max length of top users in a cluster
    - core_detector is a JaccardCoreDetector, we can inject it before calling this function
    """

    # for each child
    path = DEFAULT_PATH
    injector = sdi.Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    user_getter = dao_module.get_user_getter()
    for child_node in children:
        child = child_node.root

        top_user_similarity = 0  # initialize similarity of top users between child and parent to 0%
        parent_of_child = None  # initialize the suspected parent_tree of current child_tree to None

        # see which parent that child belongs to by ranking function
        for parent_node in parents:
            parent = parent_node.root

            sim = jaccard_similarity(parent_node.top_users, child_node.top_users)

            if sim > top_user_similarity:
                top_user_similarity = sim
                parent_of_child = parent_node  # Update suspected parent of current child

        # After we iterated over all parents:
        child_node.parent = parent_of_child
        # if this child does in fact have a parent:
        if parent_of_child is not None:
            parent_of_child.children.append(child_node)


#########################   Side tangent: Compute edges by similarity   ##########################
def _compute_expected_similarity(parents: List[ClusterNode],
                                 children: List[ClusterNode]) -> float:
    """
    Let p in parents, c in children, return the expected similarity for p to be the parent of c.
    """
    total_similarity = 0

    # For each parent p
    for c in children:
        cur_largest_sim = 0

        for p in parents:
            p_sim = jaccard_similarity(p.root.users, c.root.users)
            if p_sim > cur_largest_sim:
                cur_largest_sim = p_sim

        total_similarity += cur_largest_sim

    # After every child has found its most suitable parent
    expected_sim = total_similarity / len(children)
    return expected_sim


def construct_edges_by_similarity(parents: List[ClusterNode],
                                  children: List[ClusterNode]) -> None:
    """
    - Modify parents and children by establishing edges between them.
    - Edge is established between parent p (in parents) and child c (in children), iff, p has the highest
      user jaccard similarity with c amongst all parents, AND this similarity is equal to, or above the
      *expected similarity threshold*.

    Note: the expected similarity threshold is the expected jaccard similarity between parents and
          their most-likely child.
          -> it is the average of the similarity sum amongst all parents and their most similar child
             (where this similarity != 0).

    """

    expected_sim = _compute_expected_similarity(parents, children)
    for child_node in children:
        best_sim = 0
        parent_of_child = None

        for parent_node in parents:
            cur_sim = jaccard_similarity(child_node.root.users, parent_node.root.users)
            if cur_sim >= expected_sim and cur_sim > best_sim:
                best_sim = cur_sim
                parent_of_child = parent_node

        # After we finished checking all parents:
        child_node.parent = parent_of_child
        if parent_of_child is not None:
            parent_of_child.children.append(child_node)


##################################################################################################


def package_cluster_nodes(base_user: str, clusters: List[Cluster], thresh, ranked=False) -> List[ClusterNode]:
    """
    Package every cluster in clusters into a ClusterTree with no parent and no child.

    The threshold used to generate the clusters (thresh), is recorded in the tree nodes,
    we do this for the sake of convenience in future visualizations & testing.
    """
    trees = []
    for c in clusters:
        if ranked:
            top_users = rank.rank_users(base_user, c)
        else:
            top_users = None
        tree = ClusterNode(thresh=thresh, root=c, top_users=top_users)
        c.top_users = top_users
        trees.append(tree)

    return trees


def get_main_roots(all_nodes: List[ClusterNode]) -> List[ClusterNode]:
    """
    Return a list containing every node from all_nodes that have no parent, we call each
    such node a "main_root".
    """
    result = []
    for n in all_nodes:
        if n.parent is None:
            result.append(n)

    return result


def visualize_forest(all_nodes: List[ClusterNode]) -> None:
    """
    Visualize the entire forest, where all_nodes contains all the nodes in the forest
    """
    main_roots = get_main_roots(all_nodes)
    assert (len(main_roots) != 0)
    # If we can't find any main_roots in our forest, then something is wrong since a tree must be rooted somewhere
    G = pgv.AGraph(strict=False, directed=True)
    for i, main_root in enumerate(main_roots):
        # main_root.display()
        main_root.display_cluster(G, str(i))
    G.layout(prog='dot')  # use dot
    G.draw('graph.png')


def visualize_forest1(screen_name: str, main_roots: List[ClusterNode], iter: Optional[int]) -> None:
    """
    Visualize the entire forest, where all_nodes contains all the nodes in the forest
    """
    assert (len(main_roots) != 0)
    # If we can't find any main_roots in our forest, then something is wrong since a tree must be rooted somewhere
    img_path = f"trees2/{screen_name[:6]}_tree_{iter}.png"
    file_path = f"trees2/{screen_name[:6]}_cluster_nodes_{iter}.txt"

    G = pgv.AGraph(strict=False, directed=True)
    for i, main_root in enumerate(main_roots):
        # main_root.display()
        main_root.display_cluster(G, str(i), file_path)
    with open(file_path, "a") as f:
        f.write("--------------------\n")
        f.close()
    G.layout(prog='dot')  # use dot
    G.draw(img_path)


def _get_core_detector(user_activity: str):
    """
    This is a convenient helper function to get a JaccardCoreDetector
    """
    log = LoggerFactory.logger(__name__)
    DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/detect_core_config.yaml"
    try:
        injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
        process_module = injector.get_process_module()
        core_detector = process_module.get_jaccard_core_detector(user_activity)
        return core_detector
    except Exception as e:
        log.exception(e)
        exit()


def _initialize_nodes(soc_graph, neighbourhood, user: str, cur_thresh: float, user_activity: str) -> List[ClusterNode]:
    """
    Return a list of nodes, each representing a cluster, given a <user> and the corresponding
    social graph <soc_graph> and local neighbourhood <neighbourhood>, where the social graph is
    refined under threshold <cur_thresh>.
    """
    # Refine the social graph with cur_thresh
    refined_social_graph = \
        csgc.refine_social_graph_jaccard_users(user, soc_graph, neighbourhood, user_activity, threshold=cur_thresh)

    # generate the clusters
    clusters = csgc.clustering_from_social_graph(user, refined_social_graph)

    clusters_filtered = csgc.filter_by_expected_size(clusters)
    nodes = package_cluster_nodes(user, clusters_filtered, cur_thresh, True)

    return nodes


def clusters_to_forest(start_thresh: float,
                       end_thresh: float,
                       increment: float,
                       user: str,
                       user_activity: str) -> List[ClusterNode]:
    """
    Generate a forest where each tree node represents a cluster in the neighborhood of user.
    The tree has the following structure:

    - On root-level, each cluster is generated under threshold start_thresh.
    - On each subsequent level, the starting threshold is incremented by increment, to generate the clusters on
      that level.
    - Edges between each level and its subsequent level are drawn by similarities among their top users
    - The levels continue until we reach the smallest threshold >= end_thresh

    We return a list containing all the tree nodes within the forest.

    Preconditions:
    - 0 <= start_thresh < end_thresh <= 1
    - start_thresh <= (end_thresh - increment)  # To ensure the forest has at least 2 levels
    - increment != 0
    """
    assert (0 < start_thresh < end_thresh < 1)
    assert (increment != 0)
    assert (start_thresh + increment < end_thresh)

    # Print some important info
    print(f"Computing the forest starting from threshold: {start_thresh}\n"
          f"ending at threshold: {end_thresh}\n"
          f"increment threshold by {increment} each time\n")

    # Keep track of all the nodes in the forest, so that we can find main_roots later
    all_nodes = []

    soc_graph, neighbourhood = csgc.create_social_graph(user, user_activity)
    cd = _get_core_detector(user_activity)
    cur_thresh = start_thresh

    # === Parent ===
    # Generate the cluster nodes on parent level (for 1st iteration)
    parent_nodes = _initialize_nodes(soc_graph, neighbourhood, user, cur_thresh, user_activity)

    # add to the entire node collection
    all_nodes.extend(parent_nodes)

    while cur_thresh <= (end_thresh - increment):
        print(f"Currently comparing thresholds: {cur_thresh} <-> {cur_thresh + increment}")

        # === Child ===
        # Update cur_thresh to consider the child level
        cur_thresh += increment

        # Generate the cluster nodes on child level
        child_nodes = _initialize_nodes(soc_graph, neighbourhood, user, cur_thresh, user_activity)

        # add to the entire node collection
        all_nodes.extend(child_nodes)

        # Draw edges between the 2 levels
        # TODO: There are currently 2 ways to draw edges, we want to allow the user to choose which
        #  way they wish to use in the top-level interface.
        construct_edges_by_topuser(cd, parents=parent_nodes, children=child_nodes)
        # construct_edges_by_similarity(parents=parent_nodes, children=child_nodes)

        # The children become the new parents (new generation begins)
        parent_nodes = child_nodes

    return all_nodes


def dividing_social_graph(start_thresh: float,
                          end_thresh: float,
                          increment: float,
                          user: str,
                          user_activity: str) -> List[ClusterNode]:
    assert (0 < start_thresh < end_thresh < 1)
    assert (increment != 0)
    assert (start_thresh + increment < end_thresh)

    # Print some important info
    print(f"Dividing the social graphs into forest starting from threshold: {start_thresh}\n"
          f"ending at threshold: {end_thresh}\n"
          f"increment threshold by {increment} each time\n")
    print(f"User name: {user}\n")

    # Keep track of all the nodes in the forest, so that we can find main_roots later

    soc_graph, neighbourhood = csgc.create_social_graph(user, user_activity=user_activity)
    refined_soc_graph = \
        csgc.refine_social_graph_jaccard_users(user, soc_graph,
                                               neighbourhood, user_activity, threshold=start_thresh)
    top_nodes = generate_clusters(user, refined_soc_graph, neighbourhood,
                                  start_thresh, increment, end_thresh, user_activity)
    return top_nodes


def generate_soc_graph_and_neighbourhood_from_cluster(node: ClusterNode, neighbourhood: LocalNeighbourhood,
                                                      user_activity) -> tuple:
    cluster = node.root
    user_map = {}
    for user in cluster.users:
        user_map[user] = list(set(neighbourhood.get_user_activities(user)).intersection(
            cluster.users)) if user_activity == 'friends' else neighbourhood.get_user_activities(user)

    #base_user_activities = user_map[str(cluster.base_user)]
    cluster_neighbourhood = \
        LocalNeighbourhood(cluster.base_user, None, user_map, neighbourhood.user_activity)
    cluster_soc_graph = \
        csgc.create_social_graph_from_local_neighbourhood(cluster_neighbourhood, user_activity)
    return cluster_neighbourhood, cluster_soc_graph  #, base_user_activities


def generate_clusters(base_user: str, soc_graph,
                      neighbourhood: LocalNeighbourhood,
                      thresh: float, increment: float, end_thresh: float,
                      user_activity: str,
                      just_first_level: bool = False) -> List[ClusterNode]:
    if thresh > end_thresh:
        return []

    # === Parent ===
    # Generate the cluster nodes on parent level (for 1st iteration)

    # generate the clusters
    # log.info(f"Social graph users: {list(soc_graph.graph.nodes)}")
    clusters = csgc.clustering_from_social_graph(base_user, soc_graph)
    # Intersection of users in clusters
    # ref_set = set([-1]) if len(clusters) <= 1 else set(clusters[0].users)
    # for cluster in clusters:
    #     ref_set = ref_set.intersection(set(cluster.users))
    # log.info(f"Intersection of users in clusters: {ref_set}")

    clusters_filtered = csgc.filter_by_expected_size(clusters)
    # Set ranked=True when visualizing tree
    parent_nodes = package_cluster_nodes(base_user, clusters_filtered, thresh, ranked=True)
    if just_first_level:
        return parent_nodes
    thresh += increment
    for parent_node in parent_nodes:
        cluster_neighbourhood, cluster_soc_graph = \
            generate_soc_graph_and_neighbourhood_from_cluster(parent_node,
                                                              neighbourhood, user_activity)
        if cluster_neighbourhood == neighbourhood:
            continue
        refined_cluster_soc_graph = \
            csgc.refine_social_graph_jaccard_users(base_user, cluster_soc_graph,
                                                   cluster_neighbourhood,
                                                   user_activity,
                                                   threshold=thresh)
        # cluster_neighbourhood.users[str(parent_node.root.base_user)] = base_user_activities
        child_nodes = generate_clusters(base_user, refined_cluster_soc_graph,
                                        cluster_neighbourhood,
                                        thresh, increment, end_thresh,
                                        user_activity)
        # Intersection in the child nodes
        # ref_set = set(-1)
        # if len(child_nodes) > 1:
        #     ref_set = set(child_nodes[0].root.users)
        for child_node in child_nodes:
            # ref_set = ref_set.intersection(set(child_node.root.users))
            child_node.parent = parent_node
            # if this child does in fact have a parent:
            parent_node.children.append(child_node)
        # log.info(f"Parent size: {len(parent_node.root.users)}")
        # log.info(f"Ref set: {list(ref_set)}")
    return parent_nodes


def _has_no_split(root: ClusterNode) -> bool:
    """
    Return true iff the tree rooted at root has no divergence.
    i.e. each node in the tree has <= 1 child
    """
    if len(root.children) > 1:
        return False

    if len(root.children) == 0:
        # if this tree is a leaf (which has < 1 child, hence <= 1 child)
        return True

    # else, root has exactly 1 child
    return _has_no_split(root.children[0])


def trace_no_split_nodes(roots: List[ClusterNode]) -> List[ClusterNode]:
    """
    Let a "longest non-divergent path" denote any subtree in the forest, such that:
    - it is a path from node A to B without any divergence in between, and
    - it is the longest such path that passes nodes A and B.

    For example:
         A
        / \
       B   C
      /
     D

    In the above graph, "B-D" and "C" are the longest non-divergent paths.

    Return a list of tree nodes, where each node is the first node in some longest non-divergent path
    within our forest.
    - Each tree in our forest is rooted at a node in roots
    """
    result = []

    for root in roots:
        # if root has no splitting
        if _has_no_split(root):
            result.append(root)

        # else, we trace to the children of this root
        else:
            result.extend(trace_no_split_nodes(root.children))

    return result


def trace_no_redundant_nodes(roots: List[ClusterNode]) -> List[ClusterNode]:
    """
    Let a "longest non-divergent path" denote any subtree in the forest, such that:
    - it is a path from node A to B without any divergence in between, and
    - it is the longest such path that passes nodes A and B.

    For example:
         A
        / \
       B   C
      /
     D

    In the above graph, "B-D" and "C" are the longest non-divergent paths.

    Return a list of tree nodes, where each node is the first node in some longest non-divergent path
    within our forest.
    - Each tree in our forest is rooted at a node in roots
    """
    result = []

    for root in roots:
        # if root has no splitting
        result.append(root)
        if not _has_no_split(root):
            result.extend(trace_no_redundant_nodes(root.children))

    return result


def clustering_from_social_graph(screen_name: str, user_activity: str, iter: Optional[int]) -> List[Cluster]:
    """Returns clusters from the social graph and screen name of user."""
    try:
        log.info("Clustering:")
        #all_nodes = clusters_to_forest(0.3, 0.60, 0.05, screen_name)
        #main_roots = get_main_roots(all_nodes)
        # We set lower thresholds for non-friend activities
        main_roots = dividing_social_graph(0.0001, 0.001, 0.0003, screen_name, user_activity=user_activity)
        # main_roots = dividing_social_graph(0.0005, 0.005, 0.0015, screen_name, user_activity=user_activity)
        # main_roots = dividing_social_graph(0.005, 0.01, 0.001, screen_name, user_activity=user_activity)
        # main_roots = dividing_social_graph(0.03, 0.6, 0.05, screen_name, user_activity="friends")
        # visualize_forest1(screen_name, main_roots, iter)
        # no_split_nodes = trace_no_split_nodes(main_roots)
        no_redundant_nodes = trace_no_redundant_nodes(main_roots)
        clusters = []

        def traverse_tree(node: ClusterNode):
            clusters.append(node.root)
            if len(node.children) == 0:
                return
            for child in node.children:
                traverse_tree(child)

        for n in no_redundant_nodes:
            # n.root is the cluster at the node n
            # traverse_tree(n)
            clusters.append(n.root)
        return clusters
    except Exception as e:
        log.exception(e)
        exit()


if __name__ == "__main__":
    # Find the no_split_nodes for a particular user, given some starting threshold, some finishing threshold,
    # and an increment.
    # timnitGebru
    #all_nodes = clusters_to_forest(0.3, 0.6, 0.05, "fchollet", "friends")
    top_nodes = dividing_social_graph(0.001, 0.01, 0.002, "chessable", "user retweets")
    #top_nodes = dividing_social_graph(0.3, 0.6, 0.05, "hardmaru", "friends")
    #visualize_forest(all_nodes)
    # visualize_forest1(top_nodes)
    # Find the oldest nodes in any longest non-divergent path in our resulting forest
    print("============================================================")
    print("The leading nodes in longest non-divergent paths are:")
    main_roots = top_nodes
    #main_roots = get_main_roots(all_nodes)
    no_split_nodes = trace_no_split_nodes(main_roots)

    for n in no_split_nodes:
        path = DEFAULT_PATH
        cluster = n.root
        injector = sdi.Injector.get_injector_from_file(path)
        dao_module = injector.get_dao_module()
        user_getter = dao_module.get_user_getter()
        base_user = user_getter.get_user_by_id(cluster.base_user)
        users = []
        for user in cluster.users:
            users.append(user_getter.get_user_by_id(user).screen_name)
        users.sort()
        top_10 = n.top_users
        print(f"Top 10 users in the cluster {n.id} by intersection ranking:")
        print(top_10)

    # Want to visually confirm that, these are the leading nodes of the longest non-divergent paths

    # print("============================================================")
    # print("The leading nodes in longest non-divergent paths are:")

    # for n in all_nodes:
    #     if len(n.children) == 0:
    #         soc_graph, neighbourhood = csgc.create_social_graph("fchollet")
    #         cluster_neighbourhood, cluster_soc_graph, base_user_friends = \
    #             generate_soc_graph_and_neighbourhood_from_cluster(n,
    #                                                               neighbourhood)
    #         cluster_neighbourhood.users[str(n.root.base_user)] = base_user_friends
    #         refined_soc_graph = \
    #             csgc.refine_social_graph_jaccard_users("fchollet", cluster_soc_graph,
    #                                                    cluster_neighbourhood, threshold=n.threshold)
    #         top_nodes = generate_clusters("fchollet", refined_soc_graph,
    #                                       cluster_neighbourhood,
    #                                       n.threshold, 0.05, 0.8)
    #         visualize_forest1(top_nodes)
