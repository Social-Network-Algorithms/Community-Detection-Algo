from src.dao.local_neighbourhood_from_RT_users.getter.local_neighbourhood_getter import LocalNeighbourhoodGetter
from src.model.local_neighbourhood import LocalNeighbourhood


class MongoLocalNeighbourhoodGetter(LocalNeighbourhoodGetter):
    def __init__(self):
        self.collection = None

    def set_collection(self, collection) -> None:
        self.collection = collection

    def get_local_neighbourhood(self, seed_id: str, params=None):
        doc = None
        if params is None:
            doc = self.collection.find_one({"seed_id": str(seed_id)})
        else:
            doc = self.collection.find_one({
                "seed_id": str(seed_id),
                "params": params})
        return LocalNeighbourhood.fromDict(doc)
