
class Clusterer():
    def __init__(self, social_graph_getter, cluster_setter, user_friend_getter):
        self.social_graph_getter = social_graph_getter
        self.cluster_setter = cluster_setter
        self.user_friend_getter = user_friend_getter

    def cluster(self, seed_id, params):
        raise NotImplementedError("Subclasses should implement this")
