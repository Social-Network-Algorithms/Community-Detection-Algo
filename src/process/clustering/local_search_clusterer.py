from src.process.clustering.clusterer import Clusterer
from src.model.cluster import Cluster
from src.shared.logger_factory import LoggerFactory
from src.process.clustering.LocalSearch.LS_algorithm import hierarchical_degree_communities
import networkx as nx
from networkx.utils import groups, not_implemented_for, py_random_state

log = LoggerFactory.logger(__name__)

class LocalSearchClusterer(Clusterer):
    def cluster(self, seed_id, params):
        social_graph = self.social_graph_getter.get_social_graph(seed_id, params)
        self.cluster_by_social_graph(seed_id, social_graph, params)

    def cluster_by_social_graph(self, seed_id, social_graph, params):
        graph_for_LS = social_graph.graph.to_undirected()
        nodes = list(graph_for_LS.nodes())
        mapping = {nodes[i]: i for i in range(len(nodes))}
        graph_for_LS = nx.relabel_nodes(graph_for_LS, mapping)

        def reverse_mapping(mapping, values):
            return [key for key, value in mapping.items() if value in values]
        
        D,center_dcd,y_dcd,y_partition,plot_combination_data = hierarchical_degree_communities(graph_for_LS, auto_choose_centers=True, maximum_tree=False, seed=1, plot=False)
        # auto_choose_centers chooses the number of clusters, then takes the max with center_num
        log.info("center_dcd:")
        log.info(reverse_mapping(mapping, center_dcd))
        """
        y_partition of the form: {node: community_center}. Let nodes with the same community_center be in the same cluster.
        """
        clusters = []
        for center in center_dcd:
            # Get users with the same center
            users = reverse_mapping(y_partition, [center]) # still in mapping form
            users = reverse_mapping(mapping, users)
            cluster = Cluster(seed_id, users)
            clusters.append(cluster)
            log.info(len(cluster.users))

        log.info("Number of clusters " + str(len(clusters)))
        self.cluster_setter.store_clusters(seed_id, clusters, params)
        return clusters