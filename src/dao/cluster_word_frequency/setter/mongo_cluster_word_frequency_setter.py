from typing import List, Dict
from src.dao.cluster_word_frequency.setter.cluster_word_frequency_setter import ClusterWordFrequencySetter


class MongoClusterWordFrequencySetter(ClusterWordFrequencySetter):
    def __init__(self):
        self.cluster_word_frequency_collection = None

    def set_cluster_word_frequency_collection(self, cluster_word_frequency_collection: str) -> None:
        self.cluster_word_frequency_collection = cluster_word_frequency_collection

    def store_cluster_word_frequency_vector(self, user_ids: List[str], cluster_word_freq_vc: Dict):
        doc = { "user_ids": user_ids, "word_count": sum(cluster_word_freq_vc.values()),"word_frequency_vector": cluster_word_freq_vc}

        if self._contains_user(user_ids):
            self.cluster_word_frequency_collection.find_one_and_replace({"user_ids": user_ids}, doc)
        else:
            self.cluster_word_frequency_collection.insert_one(doc)

    def _contains_user(self, user_ids) -> bool:
        return self.cluster_word_frequency_collection.find_one({"user_ids": user_ids}) is not None



    