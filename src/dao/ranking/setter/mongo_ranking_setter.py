from src.dao.ranking.setter.ranking_setter import RankingSetter
from src.dao.mongo.mongo_dao import MongoDAO
from src.model.ranking import Ranking


class MongoRankingSetter(RankingSetter, MongoDAO):
    """
    An abstract class representing an object that stores tweets in a
    datastore
    """

    def store_ranking(self, ranking):
        if self._contains_ranking(ranking):
            self.collection.find_one_and_replace({"seed_id": str(ranking.seed_id), "params": ranking.params}, ranking.__dict__)
        else:
            self.collection.insert_one(ranking.__dict__)

    def _contains_ranking(self, ranking: Ranking) -> bool:
        return self.collection.find_one({"seed_id": str(ranking.seed_id),
                                         "params": ranking.params}) is not None
