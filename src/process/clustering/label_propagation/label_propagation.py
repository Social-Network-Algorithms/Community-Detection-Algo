import re
import sys

from networkx.algorithms.community.modularity_max import greedy_modularity_communities
from networkx.algorithms.community.label_propagation import label_propagation_communities
from datetime import datetime
from typing import List, Tuple, Union, Dict
from src.model.cluster import Cluster


class LabelPropagation():
    def gen_clusters(self, user_id, social_graph_getter, label_prop_cluster_setter):
        user_friends_graph = social_graph_getter.get_social_graph(user_id)
        cluster_list = self.get_clusters(user_id, user_friends_graph.graph)  # doesnot work for the directed graph in SocialGraph object
        label_prop_cluster_setter.store_clusters(user_id, cluster_list)
        return cluster_list

    def get_clusters(self, base_user, user_friends_graph, method="") -> List[Cluster]: # TODO:
        """
        Return a dictionary representation of the clusters of the local graph.
        """
        if method=="modularity":
            community_data = greedy_modularity_communities(user_friends_graph)
        else:
            community_data = [item for item in label_propagation_communities(user_friends_graph)]
        d = {}
        for i in range(len(community_data)):
            if base_user in community_data[i]:
                li = list(community_data[i])
                li.pop(li.index(base_user))
                li.insert(0, base_user)
                d[i] = li
            else:
                d[i] = [base_user] + list(community_data[i])

        # Flatten dict into cluster list
        cluster_list = [d[k] for k in d]
        print("Number of clusters " + str(len(cluster_list)))

        return cluster_list















    # def __init__(self) -> None:
    #     # A graph representing the local neighborhood of a particular user
    #     self.graph = nx.Graph()
    #     self.base_user = Non

#     def match_community_to_keywords(self, community: str) -> List:
#         """
#         Returns the cluster of the local neighborhood that mostly closely corresponds to the keyword information
#         given by the community name.
#         """
#         d = self.get_clusters()
#         db = database_handler.DatabaseHandler()
#         keywords = db.get_keywords(community)
#         max_similarity_community = None
#         argmax_similarity_community = 0
#         for key in d.keys():
#             similarity_score = 0
#             num_tweets = 0
#             for user in d[key]:
#                 retweets, tweets = db.get_tweets(user, START_TIME, END_TIME)
#                 all_tweets = [retweet[0] for retweet in retweets] + tweets
#                 num_tweets += len(all_tweets)
#                 for tweet in all_tweets:
#                     if keywords_in_tweet(tweet, keywords):
#                         similarity_score += 1

#             similarity_score = 0 if num_tweets==0 else similarity_score/num_tweets

#             print('cluster being tested', max_similarity_community, 'score', similarity_score)

#             if argmax_similarity_community < similarity_score:
#                 max_similarity_community = d[key] if self.base_user in d[key] else d[key] + [self.base_user]
#                 argmax_similarity_community = similarity_score

#         #TODO remove from final product
#         print('max similarity community', max_similarity_community, 'score', similarity_score)
#         return max_similarity_community


# def keywords_in_tweet(tweet: str, keywords: List[str]) -> bool:
#     """
#     Helper function that returns true if a filtered version of a given tweet contains
#     a word in the set of keywords.
#     """
#     for keyword in keywords:
#         # A bit diff from sarah's regex but close enough
#         re_keyword = r'(?i)\b' + keyword + r's?\b'
#         if re.search(re_keyword, tweet) is not None:
#             return True
#     return False

# if __name__=="__main__":
#     lg = LocalGraph()
#     lg.generate_from_user("animesh_garg")
#     # clusters = lg.get_clusters(method='lprop')
#     # print(clusters)
