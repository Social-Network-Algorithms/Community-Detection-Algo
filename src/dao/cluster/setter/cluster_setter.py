from typing import List

from src.model.cluster import Cluster

class ClusterSetter:
    def store_clusters(self, seed_id: str, clusters: List[Cluster], params):
        raise NotImplementedError("Subclasses should implement this")
