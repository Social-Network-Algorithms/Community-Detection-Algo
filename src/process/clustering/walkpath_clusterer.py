from src.process.clustering.clusterer import Clusterer
from src.model.cluster import Cluster
from src.shared.logger_factory import LoggerFactory

from collections import Counter

import networkx as nx
from networkx.utils import groups, not_implemented_for, py_random_state

class WalkpathClusterer(Clusterer):
    def cluster(self, seed_id, params):
        pass