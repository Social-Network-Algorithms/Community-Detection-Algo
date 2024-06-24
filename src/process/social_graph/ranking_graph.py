import networkx as nx
from src.scripts.cluster_ranking_experiments import jaccard_similarity

class RankingGraph():
    """
    Creates a graph of bluesky friends representing a community
    """

    def gen_user_friends_graph(self, users, local_friends):
        """
        Generates a user friends graph for a given user

        @param users the user to generate the graph for

        """
        user_friends_graph = self.get_user_friends_graph(users, local_friends)

        return user_friends_graph

    def get_user_friends_graph(self, users, local_friends) -> nx.Graph:
        """
        Constructs the social graph of a given user, assuming that the users local
        neighbourhood has already been stored, and is accessible from user_friends_getter

        @param user the user to generate the graph for
        @param user_friends_getter the dao to retrieve the user's friends from

        @return the social graph of the user's local neighbourhood
        """
        graph = nx.Graph()

        for agent in users:
            graph.add_node(agent)

        # Edges between user1 and user2 indicate that both users local following
        # sets that have Jaccard similarity >= 0.1

        for user1 in users:
            for user2 in users:
                lst1 = local_friends[user1]
                lst2 = local_friends[user2]
                if jaccard_similarity(lst1, lst2) >= 0.1 and user1 != user2:
                    graph.add_edge(user1, user2)

        return graph
