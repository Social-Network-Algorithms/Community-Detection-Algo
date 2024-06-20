from src.dao.local_neighbourhood_from_RT_users.setter.local_neighbourhood_setter import LocalNeighbourhoodSetter
from src.model.local_neighbourhood import LocalNeighbourhood


class MongoLocalNeighbourhoodSetter(LocalNeighbourhoodSetter):
    def __init__(self):
        self.collection = None

    def set_collection(self, collection) -> None:
        self.collection = collection

    def store_local_neighbourhood(self, local_neighbourhood: LocalNeighbourhood):
        if self._contains_local_neighbourhood(local_neighbourhood):
            self.collection.find_one_and_replace({"seed_id": str(local_neighbourhood.seed_id),
                                                  "params": local_neighbourhood.params}, local_neighbourhood.__dict__)
        else:
            self.collection.insert_one(local_neighbourhood.__dict__)

    def _contains_local_neighbourhood(self, local_neighbourhood: LocalNeighbourhood):
        return self.collection.find_one({"seed_id": str(local_neighbourhood.seed_id), "params": local_neighbourhood.params}) is not None
