from typing import List, Dict

class ClusterRelativeWordFrequencySetter:
    """
    An abstract class representing an object that stores a clusters word frequency vector in a datastore
    """

    def store_cluster_relative_word_frequency_vector(self, user_ids:List[str], cluster_relative_word_freq_vc: Dict):
        raise NotImplementedError("Subclasses should implement this")