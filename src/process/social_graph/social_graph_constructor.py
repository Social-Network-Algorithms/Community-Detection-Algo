from src.model.social_graph.union_social_graph import UnionSocialGraph
from src.model.social_graph.intersection_social_graph import IntersectionSocialGraph
from src.dao.social_graph.setter.social_graph_setter import SocialGraphSetter
from src.dao.local_neighbourhood.getter.local_neighbourhood_getter import LocalNeighbourhoodGetter


class SocialGraphConstructor():
    """
    Creates a graph of bluesky friends representing a community
    """

    def __init__(self, local_neighbourhood_getter: LocalNeighbourhoodGetter, social_graph_setter: SocialGraphSetter):
        self.local_neighbourhood_getter = local_neighbourhood_getter
        self.social_graph_setter = social_graph_setter

    def construct_social_graph(self, seed_id, params=None, is_union=True, remove_unconnected_nodes=True):
        local_neighbourhood = self.local_neighbourhood_getter.get_local_neighbourhood(seed_id, params)
        return self.construct_social_graph_from_local_neighbourhood(local_neighbourhood, params=params, is_union=is_union)

    def construct_social_graph_from_local_neighbourhood(self, local_neighbourhood, params=None, is_union=True, remove_unconnected_nodes=True):
        social_graph = None
        if is_union:
            social_graph = UnionSocialGraph.fromLocalNeighbourhood(local_neighbourhood, remove_unconnected_nodes=remove_unconnected_nodes)
        else:
            social_graph = IntersectionSocialGraph.fromLocalNeighbourhood(local_neighbourhood, remove_unconnected_nodes=remove_unconnected_nodes)

        self.social_graph_setter.store_social_graph(social_graph)
        return social_graph
    
    def construct_weighted_social_graph_from_local_neighbourhood(self, local_neighbourhood, weights_map, params=None, is_union=True, remove_unconnected_nodes=True):
        social_graph = None
        if is_union:
            social_graph = UnionSocialGraph.fromLocalNeighbourhood(local_neighbourhood,
            params={"weighted": True}, weights_map=weights_map,
            remove_unconnected_nodes=remove_unconnected_nodes)
        else:
            social_graph = IntersectionSocialGraph.fromLocalNeighbourhood(local_neighbourhood,
            params={"weighted": True}, weights_map=weights_map,
            remove_unconnected_nodes=remove_unconnected_nodes)

        self.social_graph_setter.store_social_graph(social_graph)
        return social_graph
