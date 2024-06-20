from src.model.cluster_word_frequency_vector import ClusterWordFrequencyVector
from src.dao.cluster_relative_word_frequency.getter.cluster_relative_word_frequency_getter import ClusterRelativeWordFrequencyGetter


class MongoClusterRelativeWordFrequencyGetter(ClusterRelativeWordFrequencyGetter):
    def __init__(self):
        self.cluster_relative_word_frequency_collection = None

    def set_cluster_relative_word_frequency_collection(self, cluster_relative_word_frequency_collection: str) -> None:
        self.cluster_relative_word_frequency_collection = cluster_relative_word_frequency_collection

    def get_cluster_relative_word_frequency_by_ids(self, user_ids: str) -> ClusterWordFrequencyVector:
        doc = self.cluster_relative_word_frequency_collection.find_one({"user_ids": [str(user_id)] for user_id in user_ids})
        if doc is not None:
            users_dict = {"user_id": user_ids, "word_frequency_vector": doc["word_frequency_vector"] }
            return ClusterWordFrequencyVector.fromDict(users_dict)

        return doc