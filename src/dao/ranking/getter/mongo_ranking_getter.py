from src.dao.ranking.getter.ranking_getter import RankingGetter
from src.model.ranking import Ranking

class MongoRankingGetter(RankingGetter):
    def __init__(self):
        self.collection = None

    def set_collection(self, collection) -> None:
        self.collection = collection

    def get_ranking(self, seed_id: str, params=None):
        doc = None
        if params is None:
            doc = self.collection.find_one({"seed_id": str(seed_id)})
        else:
            doc = self.collection.find_one({
                "seed_id": str(seed_id),
                "params": params})

        new_doc = {"seed_id": seed_id, "ids": doc["ids"], "params": params}
        return Ranking.fromDict(new_doc)
