from typing import List
from collections import Counter

def cluster_relative_frequency(user_to_rwf, cluster) -> Counter:
    rwf_list = []
    for user in user_to_rwf:
        if user['user_id'] in cluster:
            rwf_list.append(Counter(user['relative_word_frequency_vector']))

    return sum(rwf_list, Counter())

def get_clusters_most_common_words(most_common_clusters, cluster_rwf_list):
    # for each of the 5 cluster relative wf, get the top 20 words
    cluster_most_common_words = []
    for cluster_rwf in cluster_rwf_list:
        most_common_words = []
        for item in cluster_rwf.most_common(20):
            most_common_words.append(item[0])
        cluster_most_common_words.append(most_common_words)
    return cluster_most_common_words

def get_largest_cluster(cluster_list) -> List:
    """
    Return the cluster that has the most users in it.
    """
    max_size = 0
    largest_cluster = []
    for cluster in cluster_list:
        if len(cluster) > max_size:
            largest_cluster = cluster
            max_size = len(cluster)

    return largest_cluster
