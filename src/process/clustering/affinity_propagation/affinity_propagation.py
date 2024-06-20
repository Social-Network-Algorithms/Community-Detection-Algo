import numpy as np

from pymongo import MongoClient
from collections import Counter
from sklearn.cluster import AffinityPropagation as AP
from src.shared.utils import cosine_sim, word_overlap
from src.process.clustering.clustering_lib import *

class AffinityPropagation():
    def gen_clusters(self, word_freq_getter, aff_prop_setter):
        user_to_rwf = word_freq_getter.get_all_user_relative_word_frequencies()
        user_to_rwf_list = []
        for rwf in user_to_rwf:
            user_to_rwf_list.append(rwf)
        cluster_list = self.get_clusters(user_to_rwf_list)
        cluster_rwf_list = [cluster_relative_frequency(user_to_rwf_list, cluster)
                            for cluster in cluster_list]
        cluster_most_common_words = get_clusters_most_common_words(cluster_list, cluster_rwf_list)
        aff_prop_setter.store_clusters(cluster_list, cluster_rwf_list, cluster_most_common_words)
        return cluster_list, cluster_rwf_list, cluster_most_common_words

    def get_clusters(self, user_to_rwf):
        """Gets a list containing clusters of users."""
        fitted = self.get_fitted_affinity(user_to_rwf, 'cosine')
        d = {}
        li = fitted.labels_
        all_users = [doc['user_id'] for doc in user_to_rwf]
        for i in range(len(li)):
            if li[i] not in d.keys():
                d[li[i]] = [all_users[i]]
            else:
                d[li[i]].append(all_users[i])

        return list(d.values())

    def get_fitted_affinity(self, user_to_rwf, distance):
        user_to_rwf_len = len(user_to_rwf)
        aff_prop = AP(affinity='precomputed')

        similarity_mtx = np.zeros((user_to_rwf_len, user_to_rwf_len))
        if distance == 'cosine':
            i = 0
            for user1 in user_to_rwf:
                j = 0
                for user2 in user_to_rwf:
                    similarity_mtx[i][j] = cosine_sim(user1["relative_word_frequency_vector"],
                                                      user2["relative_word_frequency_vector"])
                    j += 1
                i += 1
        else:
            i = 0
            for user1 in user_to_rwf:
                j = 0
                for user2 in user_to_rwf:
                    similarity_mtx[i][j] = word_overlap(
                        user1["relative_word_frequency_vector"], user2["relative_word_frequency_vector"])
                    j += 1
                i += 1

        median = np.median(similarity_mtx)

        for i in range(user_to_rwf_len):
            similarity_mtx[i][i] = median

        return aff_prop.fit(similarity_mtx)



