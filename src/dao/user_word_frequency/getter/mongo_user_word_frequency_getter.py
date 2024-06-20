from src.model.user_word_frequency_vector import UserWordFrequencyVector
from src.dao.user_word_frequency.getter.user_word_frequency_getter import UserWordFrequencyGetter


class MongoUserWordFrequencyGetter(UserWordFrequencyGetter):
    def __init__(self):
        self.user_word_frequency_collection = None

    def get_all_user_word_frequencies(self):
        return self.user_word_frequency_collection.find()

    def get_all_user_word_frequencies_dict(self):
        uwf_dict = {}
        for doc in self.get_all_user_word_frequencies():
            user_id = doc['user_id']
            freq = doc["word_frequency_vector"]
            uwf_dict[user_id] = freq
        return uwf_dict

    def set_user_word_frequency_collection(self, user_word_frequency_collection: str) -> None:
        self.user_word_frequency_collection = user_word_frequency_collection

    def get_user_word_frequency_by_id(self, user_id: str) -> UserWordFrequencyVector:
        doc = self.user_word_frequency_collection.find_one({"user_id": str(user_id)})
        if doc is not None:
            user_dict = {"user_id": user_id, "word_frequency_vector": doc["word_frequency_vector"] }
            return UserWordFrequencyVector.fromDict(user_dict)
        else:
            user_dict = {"user_id": user_id, "word_frequency_vector": {} }
            return UserWordFrequencyVector.fromDict(user_dict)

