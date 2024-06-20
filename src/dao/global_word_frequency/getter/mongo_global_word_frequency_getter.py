from typing import List, Dict
from src.dao.global_word_frequency.getter.global_word_frequency_getter import GlobalWordFrequencyGetter


class MongoGlobalWordFrequencyGetter(GlobalWordFrequencyGetter):
    def __init__(self):
        self.global_word_frequency_collection = None

    def set_global_word_frequency_collection(self, global_word_frequency_collection: str) -> None:
        self.global_word_frequency_collection = global_word_frequency_collection

    def get_global_word_frequency(self) -> Dict:
        doc = self.global_word_frequency_collection.find({}, {"global_word_frequency_vector": 1})
        if doc is not None:
            result = None
            for item in doc:
                result = item["global_word_frequency_vector"]
            return result
        else:
            return {}
