from src.model.cluster import Cluster


class MongoClusterGetter():
    def __init__(self):
        self.collection = None

    def set_collection(self, collection) -> None:
        self.collection = collection

    def get_clusters(self, seed_id: str, params=None):
        if params is None:
            doc = self.collection.find_one({"seed_id": str(seed_id)})
        else:
            doc = self.collection.find_one({
                "seed_id": str(seed_id),
                "params": params})

        if doc is not None:
            return [Cluster.fromDict(cluster) for cluster in doc["clusters"]], doc["params"]
        return None
