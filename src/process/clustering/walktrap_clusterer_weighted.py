from src.process.clustering.clusterer import Clusterer
from src.model.cluster import Cluster
from src.shared.logger_factory import LoggerFactory

from collections import Counter

import networkx as nx
import igraph as ig

from networkx.utils import groups, not_implemented_for, py_random_state
# from cdlib import algorithms

log = LoggerFactory.logger(__name__)

class WalktrapClustererWeighted(Clusterer):
    def cluster(self, seed_id, params):
        social_graph = self.social_graph_getter.get_social_graph(seed_id, params)
        self.cluster_by_social_graph(seed_id, social_graph, params)

    def cluster_by_social_graph(self, seed_id, social_graph, params):
        clusters_data = []
        if social_graph.graph.number_of_nodes() > 0:
            # clusters_data = algorithms.walktrap(social_graph.graph).communities
            graph = ig.Graph.from_networkx(social_graph.graph) # make igraph from networkx graph
            graph.vs["name"] = graph.vs["_nx_name"]
            clustering = ig.Graph.community_walktrap(graph, graph.es['weight'], 4).as_clustering()
            for cluster in clustering:
                cluster_list_ids = []
                for node_id in cluster:
                    cluster_list_ids.append(graph.vs[node_id]["name"])
                clusters_data.append(cluster_list_ids)

        clusters = []
        for data in clusters_data:
            users = list(data)
            # log.info("Users in cluster: ", users)
            # if str(seed_id) in users: # Why is this needed?
            #     log.info("Removing seed from cluster")
            #     # log.info("Count:", users.count(str(seed_id)))
            #     users.remove(str(seed_id))

            #cleaned_users = self.clean_cluster_users(users)

            #cluster = Cluster(seed_id, cleaned_users)
            cluster = Cluster(seed_id, users)
            clusters.append(cluster)
            log.info(len(users))

        log.info("Number of clusters " + str(len(clusters)))

        self.cluster_setter.store_clusters(seed_id, clusters, params)
        return clusters
