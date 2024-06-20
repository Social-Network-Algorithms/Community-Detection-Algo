import math
import numpy
import datetime

from pymongo import MongoClient
from collections import Counter
from copy import deepcopy, copy

class MUISIConfig():
    def __init__(self, intersection_min, popularity, threshold, user_count, 
                 item_count, count, is_only_popularity):
        self.intersection_min = intersection_min 
        self.popularity = popularity
        self.threshold = threshold 
        self.user_count = user_count 
        self.item_count = item_count 
        self.count = count
        self.is_only_popularity = is_only_popularity

class MUISI():
    def __init__(self):
        self.data = MUISIData()

    def gen_clusters(self, muisi_config, user_wf_getter, user_rwf_getter, muisi_cluster_setter):
        # TODO: reminder, what is count?
        user_to_wf = user_wf_getter.get_all_user_word_frequencies_dict()
        user_to_rwf = user_rwf_getter.get_all_user_relative_word_frequencies_dict()
        user_to_items = self.data.run_uti_pipeline(user_to_rwf, user_to_wf, muisi_config)
        item_to_users = self.data.run_itu_pipeline(user_to_rwf, user_to_wf, muisi_config)
        cluster_list = self.detect_all_communities(user_to_items, item_to_users, muisi_config)
        print(user_to_items)
        print(item_to_users)
        print(cluster_list)
        muisi_cluster_setter.store_clusters(cluster_list, muisi_config)
        
        return cluster_list

    def detect_all_communities(self, user_to_items, item_to_users, muisi_config):
        id_to_cluster = {}
        count = 0
        # print(len(user_to_items))
        already_seen = []
        for user1 in user_to_items:
            for user2 in user_to_items:
                if user2 not in already_seen and user1 != user2:
                    item_intersection = list(set.intersection(
                        set(user_to_items[user1]), set(user_to_items[user2])))

                    if len(item_intersection) >= muisi_config.intersection_min:
                    # if len(item_intersection) != 0:
                        cluster = self.detect_single_community(
                            user_to_items, item_to_users, item_intersection, muisi_config.user_count, 
                            muisi_config.item_count, muisi_config.popularity, muisi_config.is_only_popularity)
                        if cluster:
                            cluster_id = cluster['users']
                            if cluster_id not in id_to_cluster:
                                # print(cluster)
                                cluster['count'] = 1
                                id_to_cluster[cluster_id] = cluster
                                count += 1
                            else:
                                id_to_cluster[cluster_id]['count'] += 1

                            # print(count)

            already_seen.append(user1)

        return [id_to_cluster[cluster_id] for cluster_id in id_to_cluster]

    def detect_single_community(self, user_to_items, item_to_users, core_items, user_count, item_count, popularity, is_only_popularity):
        # min_pop = math.ceil(popularity * item_count) # for words clustering
        min_pop = math.ceil(popularity * user_count) # for retweet clustering

        is_converged = False
        num_iterations = 0
        max_iterations = 10  # hyperparameter

        while not is_converged and num_iterations < max_iterations:
            # for word freq
            tmp_core_items = deepcopy(core_items)
            core_users = self.select(user_to_items, core_items, user_count, min_pop, is_only_popularity)
            if core_users == []:
                return None

            core_items = self.select(item_to_users, core_users, item_count, min_pop, is_only_popularity)
            if core_items == []:
                return None

            if tmp_core_items == core_items:
                is_converged = True
            
            num_iterations += 1

        core_users.sort()
        core_items.sort()
        return {'users': tuple(core_users), 'items': tuple(core_items)} if is_converged else None

    def select(self, user_to_items, core_items, count, min_pop, is_only_popularity):
        # compute the popularity of each user wrt the core_items
        user_to_popularity = Counter()
        for user in user_to_items:
            user_items = user_to_items[user]
            intersect_count = len(set.intersection(
                set(core_items), set(user_items)))
            if len(user_items) >= min_pop:
                user_to_popularity[user] = intersect_count / len(core_items)

        if is_only_popularity:
            # get the top count most popular users
            popular_users = [user for user, popularity in user_to_popularity.most_common(count)]
            if len(popular_users) != count:
                return []
            # consider tie cases
            possible_tie_value = user_to_popularity[popular_users[-1]]
            users_sorted_by_popularity = user_to_popularity.most_common()
            for i in range(count + 1, len(users_sorted_by_popularity)):
                user, popularity = users_sorted_by_popularity[i]
                if popularity == possible_tie_value:
                    popular_users.append(user)
                else:
                    return popular_users

            # popular_users.sort()
            return popular_users

        # compute the typicality of each user wrt the core_items
        user_to_typicality = Counter()
        for user in user_to_items:
            intersect_count = len(set.intersection(
                set(core_items), set(user_to_items[user])))
            user_to_typicality[user] = intersect_count / len(user_to_items[user])

        # compute the popularity and typicality rankings
        popularity_ranking = {pair[0]: rank
                            for rank, pair in enumerate(user_to_popularity.most_common())}

        typicality_ranking = {pair[0]: rank
                            for rank, pair in enumerate(user_to_typicality.most_common())}

        # compute the overall ranking for each user TODO: is there a bug with this?
        overall_ranking = Counter()
        for user in popularity_ranking:
            overall_ranking[user] = max(
                popularity_ranking[user], typicality_ranking[user])

        # TODO: consider tie cases 
        # get the top 5 overall ranking for users
        popular_users = [user[0] for user in overall_ranking.most_common()[-6:-1]]
        # popular_users = [user[0] for user in overall_ranking.most_common(5)]
        # for user in popular_users:
        # print(overall_ranking[user])
        popular_users.sort()
        return popular_users

class MUISIData:
    def get_user_to_info(self, user_to_rwf, user_to_wf):
        """ 
        # >>> rwf = dao.get_rwf()
        # >>> table1 = dao.get_user_to_info(rwf)
        # >>> print(table1)
        
        {
            Table 1
            user : {word : (rwf, count)}
        }
        """
        
        user_to_info = {}

        for user in user_to_rwf:
            user_info = {}
            user_rwf = user_to_rwf[user]
            user_wf = user_to_wf[user]
            for word in user_rwf:
                rwf = user_rwf[word]
                count = user_wf[word]
                user_info[word] = (rwf, count)
            user_to_info[user] = user_info

        return user_to_info


    def get_filtered_user_to_info(self, user_to_info, factor, count):
        """ 
        # >>> rwf = dao.get_rwf()
        # >>> table1 = dao.get_user_to_info(rwf)
        # >>> table2, _ = dao.get_filtered_user_to_info(table1, 0.5, 5)
        # >>> print(table2)

        {
            Table 2
            user : {word : (rwf, count)}
        }
        """

        return self.get_filtered(user_to_info, factor, count)
        
    def get_filtered(self, user_to_info, factor, count):
        filtered_user_to_info = {}
        relevant_words = {}
        for user in user_to_info:
            filtered_user_info = {}
            user_info = user_to_info[user]
            user_rwf = Counter({word:user_info[word][0] for word in user_info})
            average_rwf = numpy.mean(
                [rwf for item, rwf in user_rwf.most_common(count)])
            threshold = factor * average_rwf
            typical_items = [word for word in user_rwf if user_rwf[word] > threshold]
            for word in typical_items:
                filtered_user_info[word] = user_info[word]
                relevant_words[word] = 1

            filtered_user_to_info[user] = filtered_user_info

        return filtered_user_to_info, relevant_words

    def get_item_to_info(self, filtered_user_to_info, relevant_words):
        """
        {
            Table 3
            word : {user : (rwf, count)}
        }
        
        # >>> rwf = dao.get_rwf()
        # >>> table1 = dao.get_user_to_info(rwf)
        # >>> table2, relevant_words = dao.get_filtered_user_to_info(table1, 0.5, 5)
        # >>> table3 = dao.get_item_to_info(table2, relevant_words)
        # >>> print(table3)
        """

        item_to_info = {}
        for user in filtered_user_to_info:
            for item in filtered_user_to_info[user]:
                if item not in item_to_info:
                    item_to_info[item] = {}
                info = filtered_user_to_info[user][item]
                item_to_info[item][user] = info

        return item_to_info
        
    def get_filtered_item_to_info(self, item_to_info, factor, count):
        """
        {
            Table 4
            Filter based on avg threshold for top x
            word : {user : (rwf, count)}
        }

        # >>> factor, count = 0.5, 5
        # >>> rwf = dao.get_rwf()
        # >>> table1 = dao.get_user_to_info(rwf)
        # >>> table2, relevant_words = dao.get_filtered_user_to_info(table1, factor, count)
        # >>> table3 = dao.get_item_to_info(table2, relevant_words)
        # >>> table4, relevant_users = dao.get_filtered_item_to_info(table3, factor, count)
        # >>> print(relevant_users)
        """
        
        # want to get the most typical users for each word
        # for each word, get the average rwf among users of this word, then filter users by threshold
        return self.get_filtered(item_to_info, factor, count)

    def get_item_to_users(self, filtered_item_to_info, top_count):
        """
        {
            Table 5
            Use table 4: for each word, get top x users by word count
            word : {user : (rwf, count)}
        }
        
        # >>> factor, count = 0.5, 5
        # >>> rwf = dao.get_rwf()
        # >>> table1 = dao.get_user_to_info(rwf)
        # >>> table2, relevant_words = dao.get_filtered_user_to_info(table1, factor, count)
        # >>> table3 = dao.get_item_to_info(table2, relevant_words)
        # >>> table4, relevant_users = dao.get_filtered_item_to_info(table3, factor, count)
        # >>> table5 = dao.get_item_to_users(table4, 5)
        # >>> print(table5)
        """

        return self.get_top_count(filtered_item_to_info, top_count)

    def get_top_count(self, filtered_item_to_info, top_count):
        item_to_users = {}
        for word in filtered_item_to_info:
            final_item_info = {}
            item_info = filtered_item_to_info[word]

            # get only the top x users by word count
            user_count = Counter({user: item_info[user][1] for user in item_info})
            top_users = [user for user, count in user_count.most_common(top_count)]
            for user in top_users:
                final_item_info[user] = item_info[user]
            item_to_users[word] = final_item_info

        return item_to_users

    def get_double_filter_user_to_info(self, filtered_user_to_info, relevant_users):
        """
        {
            Table 6
            Filter user_to_info even more so that users only are from item to users
            user : {word : (rwf, count)}
        }

        # >>> factor, count = 0.5, 5
        # >>> rwf = dao.get_rwf()
        # >>> table1 = dao.get_user_to_info(rwf)
        # >>> table2, relevant_words = dao.get_filtered_user_to_info(table1, factor, count)
        # >>> table3 = dao.get_item_to_info(table2, relevant_words)
        # >>> table4, relevant_users = dao.get_filtered_item_to_info(table3, factor, count)
        # >>> table6 = dao.get_double_filter_user_to_info(table2, relevant_users)
        # >>> print(table6)
        """
        
        return {user:filtered_user_to_info[user] for user in relevant_users}

    def get_user_to_items(self, double_filter_user_to_info, top_count):
        """
        {
            Table 7
            Filter table 6 so that we only items are the top items by count
            user : {word : (rwf, count)} maybe we also want a version that doesn't have count
        }

        # >>> factor, count = 0.5, 5
        # >>> rwf = dao.get_rwf()
        # >>> table1 = dao.get_user_to_info(rwf)
        # >>> table2, relevant_words = dao.get_filtered_user_to_info(table1, factor, count)
        # >>> table3 = dao.get_item_to_info(table2, relevant_words)
        # >>> table4, relevant_users = dao.get_filtered_item_to_info(table3, factor, count)
        # >>> table6 = dao.get_double_filter_user_to_info(table2, relevant_users)
        # >>> table7 = dao.get_user_to_items(table6, 5)
        # >>> print(table7)
        """

        return self.get_top_count(double_filter_user_to_info, top_count)

    def user_to_items(self, table6, factor, item_count):
      
        table7 = self.get_user_to_items(table6, item_count)

        return {user:Counter({item:table6[user][item][0] for item in table7[user]}) for user in table7}

    def item_to_users(self, table4, factor, user_count):
        table5 = self.get_item_to_users(table4, user_count)

        return {item:Counter({user:table4[item][user][0] for user in table5[item]}) for item in table5}
        
    def run_uti_pipeline(self, user_to_rwf, user_to_wf, muisi_config):
        table1 = self.get_user_to_info(user_to_rwf, user_to_wf)
        table2, relevant_words = self.get_filtered_user_to_info(table1, muisi_config.threshold, muisi_config.count)
        table3 = self.get_item_to_info(table2, relevant_words)
        _, relevant_users = self.get_filtered_item_to_info(table3, muisi_config.threshold, muisi_config.count)
        table6 = self.get_double_filter_user_to_info(table2, relevant_users)
        uti = self.get_user_to_items(table6, muisi_config.item_count)

        return uti

    def run_itu_pipeline(self, user_to_rwf, user_to_wf, muisi_config):
        table1 = self.get_user_to_info(user_to_rwf, user_to_wf)
        table2, relevant_words = self.get_filtered_user_to_info(table1, muisi_config.threshold, muisi_config.count)
        table3 = self.get_item_to_info(table2, relevant_words)
        table4, _ = self.get_filtered_item_to_info(table3, muisi_config.threshold, muisi_config.count)
        itu = self.get_item_to_users(table4, muisi_config.user_count)

        return itu