from src.model.user_word_frequency_vector import UserWordFrequencyVector
from src.dao.user_relative_word_frequency.getter.user_relative_word_frequency_getter import UserRelativeWordFrequencyGetter


class MongoUserRelativeWordFrequencyGetter(UserRelativeWordFrequencyGetter):
    def __init__(self):
        self.user_relative_word_frequency_collection = None

    def set_user_relative_word_frequency_collection(self, user_relative_word_frequency_collection: str) -> None:
        self.user_relative_word_frequency_collection = user_relative_word_frequency_collection

    def get_all_user_relative_word_frequencies(self):
        return self.user_relative_word_frequency_collection.find()

    def get_all_user_relative_word_frequencies_dict(self):
        rwf_dict = {}
        for doc in self.get_all_user_relative_word_frequencies():
            user_id = doc['user_id']
            freq = doc["relative_word_frequency_vector"]
            rwf_dict[user_id] = freq
        return rwf_dict

    def get_user_relative_word_frequency_by_id(self, user_id: str) -> UserWordFrequencyVector:
        doc = self.user_relative_word_frequency_collection.find_one({"user_id": str(user_id)})
        if doc is not None:
            return doc["relative_word_frequency_vector"]
        else:
            return None