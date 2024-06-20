from src.model.cluster_word_frequency_vector import ClusterWordFrequencyVector
from src.dao.cluster_word_frequency.getter.cluster_word_frequency_getter import ClusterWordFrequencyGetter


class MongoClusterWordFrequencyGetter(ClusterWordFrequencyGetter):
    def __init__(self):
        self.cluster_word_frequency_collection = None

    def set_cluster_word_frequency_collection(self, cluster_word_frequency_collection: str) -> None:
        self.cluster_word_frequency_collection = cluster_word_frequency_collection

    def get_cluster_word_frequency_by_ids(self, user_ids: str) -> ClusterWordFrequencyVector:
        user_id_list = [] 
        for user_id in user_ids:
            user_id_list.append(str(user_id))
        doc = self.cluster_word_frequency_collection.find_one({"user_ids": user_id_list})
        if doc is not None:
            users_dict = {"user_ids": user_ids, "word_frequency_vector": doc["word_frequency_vector"] }
            return ClusterWordFrequencyVector.fromDict(users_dict)
        else:
            users_dict = {"user_ids": user_ids, "word_frequency_vector": {} }
            return ClusterWordFrequencyVector.fromDict(users_dict)
    