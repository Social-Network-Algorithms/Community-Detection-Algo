import math
import numpy
import datetime

from pymongo import MongoClient
from collections import Counter
from copy import deepcopy, copy

class MUISIRetweetConfig():
    def __init__(self, intersection_min, popularity, user_count):
        self.intersection_min = intersection_min
        self.popularity = popularity 
        self.user_count = user_count

class MUISIRetweet():
    def __init__(self):
        self.data = MUISIRetweetData()

    def gen_clusters(self, muisi_retweet_config, tweet_getter, muisi_retweet_cluster_setter):
        # user_to_retweets = tweet_getter.get_user_tweets(get_retweets=True, lazy=False)

        user_to_retweets = tweet_getter.get_all_retweets_dict()
        user_to_rir = self.data.run_utr_pipeline(user_to_retweets)
        cluster_list = self.detect_all_communities(user_to_rir, muisi_retweet_config)
        muisi_retweet_cluster_setter.store_clusters(cluster_list, muisi_retweet_config)

        return cluster_list

    def detect_all_communities(self, user_to_rir, muisi_retweet_config):
        id_to_cluster = {}
        count = 0
        # print(len(user_to_items))
        already_seen = []
        for user1 in user_to_rir:
            for user2 in user_to_rir:
                if user2 not in already_seen and user1 != user2:
                    item_intersection = list(set.intersection(
                        set(user_to_rir[user1]), set(user_to_rir[user2])))

                    if len(item_intersection) >= muisi_retweet_config.intersection_min:
                    # if len(item_intersection) != 0:
                        cluster = self.detect_single_community(
                            user_to_rir, item_intersection, 
                            muisi_retweet_config.user_count, 
                            muisi_retweet_config.popularity)
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
    def detect_single_community(self, user_to_rir, core_users, user_count, popularity):
        # min_pop = math.ceil(popularity * item_count) # for words clustering
        min_pop = math.ceil(popularity * user_count) # for retweet clustering

        is_converged = False
        num_iterations = 0
        max_iterations = 10  # hyperparameter

        while not is_converged and num_iterations < max_iterations:
            # for word freq
            tmp_core_users = deepcopy(core_users)
            core_users = self.select(user_to_rir, core_users, user_count, min_pop)
            if core_users == []:
                return None

            if tmp_core_users == core_users:
                is_converged = True
            
            num_iterations += 1

        core_users.sort()
        return {'users': tuple(core_users)} if is_converged else None

    def select(self, user_to_items, core_users, count, min_pop):
        # compute the popularity of each user wrt the core_items
        user_to_popularity = Counter()
        for user in user_to_items:
            user_items = user_to_items[user]
            intersect_count = len(set.intersection(
                set(core_users), set(user_items)))
            if len(user_items) >= min_pop:
                user_to_popularity[user] = intersect_count / len(core_users)

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

class MUISIRetweetData:
    def retweet_to_id(self, user_to_retweets):
        id = 0
        retweet_to_id = {}
        for user in user_to_retweets:
            # if doc['start'] == datetime.datetime(2018, 9, 1, 0, 0, 0) and\
            #  doc['end'] == datetime.datetime(2019, 9, 1, 0, 0, 0) and user_handle == doc['handle']:
            #     words = []

            for tweet in user_to_retweets[user]:
                if tweet["text"][0] not in retweet_to_id:
                    retweet_to_id[tweet["text"][0]] = id
                    id += 1
        return retweet_to_id
    
    def user_to_tweet_id(self, user_to_retweets, retweet_to_id):       
        user_to_tweet_id = {}
        for user in user_to_retweets:
            # if doc['start'] == datetime.datetime(2018, 9, 1, 0, 0, 0) and\
            #  doc['end'] == datetime.datetime(2019, 9, 1, 0, 0, 0) and user_handle == doc['handle']:
            # words = []
            for tweet in user_to_retweets[user]:
                if user not in user_to_tweet_id:
                    user_to_tweet_id[user] = []

                retweet_id = retweet_to_id[tweet["text"][0]]
                if retweet_id not in user_to_tweet_id[user]:
                    user_to_tweet_id[user].append(retweet_id)
        return user_to_tweet_id

    def tweet_id_to_user(self, user_to_tweet_id):
        tweet_id_to_user = {}
        for user in user_to_tweet_id:
            for item in user_to_tweet_id[user]:
                if item not in tweet_id_to_user:
                    tweet_id_to_user[item] = []
                tweet_id_to_user[item].append(user)

        return tweet_id_to_user

        # store computed data to database
        # cluster_db = client['WordFreqClustering1']
        # important_info_collection = cluster_db['ImportantInfo']
        # important_info_collection.insert_one({
        #     "RetweetToID": retweet_to_id,
        #     "UserToItems": user_to_items,
        #     # "ItemToUsers": item_to_users
        # })

    def user_to_interaction_rate(self, user_to_retweet_id, tweet_id_to_user):
        '''
        f(y|user) = (# retweets y and user share) / sum{for each retweet of user}(the number of users for this retweet - 1)  
        '''

        user_to_interaction_rate = {}
        user_to_interaction_count = {}

        for user in user_to_retweet_id:
            user_interaction_rate = Counter()
            user_interaction_count = Counter()
            user_retweet_id_list = user_to_retweet_id[user]

            # get hash table of user_retweet_id
            user_retweet_hash = {}
            for retweet_id in user_retweet_id_list:
                user_retweet_hash[retweet_id] = 1

            # compute number of retweets y and user share
            for y in user_to_retweet_id:
                if user != y:
                    y_retweet_id_list = user_to_retweet_id[y]
                   
                    shared_retweet_count = 0
                    for retweet_id in y_retweet_id_list:
                        if retweet_id in user_retweet_hash:
                            shared_retweet_count += 1
                    
                    if shared_retweet_count != 0: 
                        user_interaction_rate[y] = shared_retweet_count
                        user_interaction_count[y] = shared_retweet_count
            
            # compute the number of retweeters in local neighborhood
            user_retweet_retweeter_count = 0
            for retweet_id in user_retweet_id_list:
                user_retweet_retweeter_count += len(tweet_id_to_user[retweet_id]) - 1
            
            # finish the user_interaction_rate computation
            for user_ in user_interaction_rate:
                user_interaction_rate[user_] /= user_retweet_retweeter_count
            
            if len(user_interaction_rate) != 0:
                user_to_interaction_rate[user] = user_interaction_rate
                user_to_interaction_count[user] = user_interaction_count
        
        return user_to_interaction_rate, user_to_interaction_count


    def user_to_global_interaction_rate(self, user_to_retweet_id, retweet_local_neighborhood_count):
        '''
        f(user) = # retweets of user / # retweets in local neighborhood
        '''
        
        user_to_global_interaction_rate = Counter()

        for user in user_to_retweet_id:
            user_to_global_interaction_rate[user] = len(user_to_retweet_id[user]) / retweet_local_neighborhood_count

        return user_to_global_interaction_rate

    def get_retweet_local_neighborhood_count(self, user_to_retweet_id):
        return sum([len(user_to_retweet_id[user]) for user in user_to_retweet_id])

    def user_to_relative_interaction_rate(self, user_to_interaction_rate, user_to_global_interaction_rate):
        user_to_relative_interaction_rate = {}
        
        for user in user_to_interaction_rate:
            user_relative_interaction_rate = Counter()
            user_interaction_rate = user_to_interaction_rate[user]
            user_global_interaction_rate = user_to_global_interaction_rate[user]

            for y in user_interaction_rate:
                user_relative_interaction_rate[y] = user_interaction_rate[y] / user_global_interaction_rate

            user_to_relative_interaction_rate[user] = user_relative_interaction_rate

        return user_to_relative_interaction_rate

    def user_to_rir_threshold_filtered(self, user_to_relative_interaction_rate, user_to_interaction_count, typicality_threshold, avg_count):
        user_to_rir_threshold_filtered = {}
        user_to_interaction_count_filtered = {}
        relevant_items = {}
        for user in user_to_relative_interaction_rate:
            filtered_user_rir = {}
            filtered_interaction_count = Counter()
            user_rir = user_to_relative_interaction_rate[user]
            average_rwf = numpy.mean(
                [rwf for item, rwf in user_rir.most_common(avg_count)])
            threshold = typicality_threshold * average_rwf
            typical_items = [interaction_user for interaction_user in user_rir if user_rir[interaction_user] > threshold]
            
            for interaction_user in typical_items:
                filtered_user_rir[interaction_user] = user_rir[interaction_user]
                filtered_interaction_count[interaction_user] = user_to_interaction_count[user][interaction_user]
                relevant_items[interaction_user] = 1

            user_to_rir_threshold_filtered[user] = filtered_user_rir
            user_to_interaction_count_filtered[user] = filtered_interaction_count

        return user_to_rir_threshold_filtered, user_to_interaction_count_filtered, relevant_items
            

    def user_to_rir_top_count_filtered(self, user_to_rir_threshold_filtered, user_to_interaction_count, top_count):
        user_to_rir_top_count_filtered = {}
        
        for user in user_to_rir_threshold_filtered:
            top_count_rir = Counter()
            rir_threshold_filtered = user_to_rir_threshold_filtered[user]

            top_count_interacted_users = user_to_interaction_count[user].most_common(top_count)
            for user_, count in top_count_interacted_users:
                top_count_rir[user_] = rir_threshold_filtered[user_]
            
            user_to_rir_top_count_filtered[user] = top_count_rir

        return user_to_rir_top_count_filtered

    def run_utr_pipeline(self, user_to_retweets):
        retweet_to_id = self.retweet_to_id(user_to_retweets)
        user_to_retweet = self.user_to_tweet_id(user_to_retweets, retweet_to_id)
        retweet_to_user = self.tweet_id_to_user(user_to_retweet)
        user_to_interaction_rate, user_to_interaction_count = self.user_to_interaction_rate(user_to_retweet, retweet_to_user)
        retweet_local_neighborhood_count = self.get_retweet_local_neighborhood_count(user_to_retweet)
        user_to_global_interaction_rate = self.user_to_global_interaction_rate(user_to_retweet, retweet_local_neighborhood_count)
        user_to_relative_interaction_rate = self.user_to_relative_interaction_rate(user_to_interaction_rate, user_to_global_interaction_rate)
        user_to_rir_threshold_filtered, filtered_interaction_count, _ = self.user_to_rir_threshold_filtered(user_to_relative_interaction_rate, user_to_interaction_count, 0.5, 5)
        user_to_rir_top_count_filtered = self.user_to_rir_top_count_filtered(user_to_rir_threshold_filtered, filtered_interaction_count, 5)
    
        return user_to_rir_top_count_filtered
