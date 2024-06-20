import bson
import networkx as nx
from typing import Dict, Optional
from src.model.local_neighbourhood import LocalNeighbourhood


class SocialGraph():
    """
    A Wrapper class for a networkx graph representing a local neighbourhood
    """

    def __init__(self, graph: nx.DiGraph, seed_id: str, params=None):
        self.graph = graph
        self.seed_id = seed_id
        self.params = params

    def fromLocalNeighbourhood(local_neighbourhood: LocalNeighbourhood, params: Optional[Dict] = None, remove_unconnected_nodes=True):
        raise NotImplementedError("Subclasses should implement this")

    def remove_unconnected_nodes(local_neighbourhood: LocalNeighbourhood):
        count = 1
        user_dict = local_neighbourhood.users
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

        local_neighbourhood.users = user_dict
        user_list = list(user_dict.keys())

        return user_list

    def fromDict(dict: Dict):
        adj_list = dict["adj_list"]
        graph = nx.parse_adjlist(adj_list, create_using=nx.DiGraph)

        seed_id = dict["seed_id"]
        params = dict["params"]

        social_graph = SocialGraph(graph, seed_id, params)

        return social_graph

    def toBSON(self):
        doc = {
            "seed_id": str(self.seed_id),
            "params": self.params,
            "adj_list": list(nx.generate_adjlist(self.graph))
        }

        return doc
