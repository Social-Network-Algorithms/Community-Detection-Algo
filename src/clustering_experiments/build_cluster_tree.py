from src.clustering_experiments import create_social_graph_and_cluster as csgc
from src.model.cluster import Cluster
from src.model.cluster_tree import ClusterNode

from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
from src.model.local_neighbourhood import LocalNeighbourhood
from typing import List
from src.clustering_experiments import ranking_users_in_clusters as rank
import pygraphviz as pgv

log = LoggerFactory.logger(__name__)
DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def package_cluster_nodes(base_user: str, clusters: List[Cluster], thresh, ranked=False) -> List[ClusterNode]:
    """
    Package every cluster in clusters into a ClusterTree with no parent and no child.

    The threshold used to generate the clusters (thresh), is recorded in the tree nodes,
    we do this for the sake of convenience in future visualizations & testing.
    """
    trees = []
    for c in clusters:
        if ranked:
            top_users = rank.rank_users(c)
        else:
            top_users = None
        tree = ClusterNode(thresh=thresh, root=c, top_users=top_users)
        c.top_users = top_users
        trees.append(tree)

    return trees


def visualize_forest1(screen_name: str, main_roots: List[ClusterNode], iter) -> None:
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


def dividing_social_graph(user: str,
                          user_activity: str = "friends") -> List[ClusterNode]:
    # Keep track of all the nodes in the forest, so that we can find main_roots later
    _, neighbourhood = csgc.create_social_graph(user, user_activity=user_activity)  # user activity is "friends"
    start_thresh = 0.4
    increment, end_thresh = 0.05, 0.55
    refined_soc_graph = \
        csgc.refine_social_graph_jaccard_users(user, None,
                                               neighbourhood, user_activity, threshold=start_thresh)
    # Print some important info
    print(f"Dividing the social graphs into forest starting from threshold: {start_thresh}\n"
          f"ending at threshold: {end_thresh}\n"
          f"increment threshold by {increment} each time\n")
    print(f"User name: {user}\n")

    top_nodes = generate_clusters(user, refined_soc_graph, neighbourhood,
                                  start_thresh, increment, end_thresh, user_activity, first_level=True)
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
                      just_first_level: bool = False,
                      first_level: bool = False) -> List[ClusterNode]:
    if thresh > end_thresh:
        return []

    # generate the clusters
    clusters = csgc.clustering_from_social_graph(base_user, soc_graph)

    clusters_filtered = csgc.filter_by_expected_size(clusters)
    if first_level and len(clusters_filtered) == 0:
        clusters_filtered = clusters

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

        child_nodes = generate_clusters(base_user, refined_cluster_soc_graph,
                                        cluster_neighbourhood,
                                        thresh, increment, end_thresh,
                                        user_activity, first_level=False)

        for child_node in child_nodes:
            child_node.parent = parent_node
            # if this child does in fact have a parent:
            parent_node.children.append(child_node)

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


def get_leaves(roots: List[ClusterNode]) -> List[ClusterNode]:
    result = []

    for root in roots:
        if _has_no_split(root):
            result.append(root)
        else:
            result.extend(get_leaves(root.children))

    return result


def clustering_from_social_graph(screen_name: str, user_activity: str, leaves: bool = False) -> List[Cluster]:
    """Returns clusters from the social graph and screen name of user."""
    try:
        log.info("Clustering:")
        # We set lower thresholds for non-friend activities
        main_roots = dividing_social_graph(screen_name, user_activity=user_activity)

        # visualize_forest1(screen_name, main_roots, 1)
        no_redundant_nodes = get_leaves(main_roots) if leaves else trace_no_redundant_nodes(main_roots)
        clusters = []

        for n in no_redundant_nodes:
            # n.root is the cluster at the node n
            clusters.append(n.root)
        return clusters
    except Exception as e:
        log.exception(e)
        exit()
