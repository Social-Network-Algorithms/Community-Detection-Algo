from src.dao.social_graph.setter.social_graph_setter import SocialGraphSetter
from src.model.social_graph.social_graph import SocialGraph


class MongoSocialGraphSetter(SocialGraphSetter):
    def __init__(self):
        self.collection = None

    def set_collection(self, collection) -> None:
        self.collection = collection

    def store_social_graph(self, social_graph: SocialGraph):
        if self._contains_social_graph(social_graph):
            self.collection.find_one_and_replace({"seed_id": str(social_graph.seed_id), "params": social_graph.params},
                                                 social_graph.toBSON())
        else:
            self.collection.insert_one(social_graph.toBSON())

    def _contains_social_graph(self, social_graph: SocialGraph):
        return self.collection.find_one({"seed_id": str(social_graph.seed_id), "params": social_graph.params}) is not None
