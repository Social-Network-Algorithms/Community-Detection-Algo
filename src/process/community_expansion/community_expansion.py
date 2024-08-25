from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter

from src.process.community_expansion.clustering_helper import *
from src.process.community_expansion.plotting_helper import graph_plots
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
import csv

log = LoggerFactory.logger(__name__)
DEFAULT_PATH = str(
    get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


class CommunityExpansionAlgorithm:
    def __init__(self, initial_seed, user_getter,
                 user_tweets_getter: UserTweetsGetter,
                 user_friend_getter,
                 retweeted_users_getter,
                 dataset_creator):
        self.user_getter = user_getter
        self.user_friend_getter = user_friend_getter
        self.dataset_creator = dataset_creator
        self.community_social_support_ranker = CommunitySocialSupportRanker(user_tweets_getter, user_friend_getter,
                                                                            None)
        self.retweeted_users_getter = retweeted_users_getter
        self.initial_seed = initial_seed

    def find_potential_candidate(self, users, num_of_candidate, threshold):
        """
        Find potential candidates from the followings of the users of the current community.
        The potential candidates can also include the users that are already in the community.
        """
        # user_map: key: candidate, value: number of follower in community
        user_map = {}
        for user_id in users:
            user_friends = self.user_friend_getter.get_user_friends_ids(user_id)
            for candidate in user_friends:
                if candidate in user_map:
                    user_map[candidate] += 1
                else:
                    user_map[candidate] = 1

        log.info("Potential candidate list: " + str(len(user_map.keys())))
        # key: number of follower in community, value: list of users
        result = {}
        for k, v in user_map.items():
            if v not in result:
                result[v] = [k]
            else:
                result[v].append(k)
        # at least threshold% user in the community are candidate's follower
        threshold_1 = len(users) * threshold
        log.info("want candidate have at least " + str(threshold_1) +
                 " followers in the community")

        candidate = []
        # whether or not there are more potential candidate than we asked for
        more_potential_candidate = True
        for i in range(len(users), -1, -1):
            if i in result:
                if len(result[i]) + len(candidate) > num_of_candidate:
                    if i >= threshold_1:
                        candidate.extend(result[i][:(num_of_candidate - len(candidate))])
                        log.info("reached to max num of candidates limit. The current length is " + str(len(candidate)))

                    else:
                        log.info("break because common user reaches the minimum")
                        more_potential_candidate = False

                    break
                else:
                    if i >= threshold_1:
                        log.info(str(len(result[i])) + " candidates has " + str(i) +
                                 " common followers in current cluster")
                        candidate.extend(result[i])

                    else:
                        log.info("break because common user reaches the minimum")
                        more_potential_candidate = False
                        break

        return candidate, more_potential_candidate

    def filter_candidates_round1(self, top_size,
                                 large_account_threshold, low_account_threshold, friends_threshold, tweet_threshold,
                                 community, candidates):
        """
        top_size: Top <top_size> users are used for measurement
        large_account_threshold: Candidate cannot have more than <large_account_threshold>% number of followers than
            average of top <top_size> users.
        low_account_threshold: Candidate cannot have less than <low_account_threshold>% number of followers than
            average of top <top_size> users.
        friends_threshold: Candidate cannot have less than <friends_threshold>% number of friends than
            average of top <top_size> users.
        tweet_threshold: Candidate cannot have less than <tweet_threshold>% number of tweets than
            average of top <top_size> users.
        community: The current community
        candidates: The potential candidates
        """
        avg_followers_large = 0
        avg_followers_small = 0
        avg_friends = 0
        avg_tweets = 0

        for j in range(top_size):
            user_id = community[j]
            user = self.user_getter.get_user_by_id(user_id)
            avg_followers_large += user.followers_count
        for j in range(top_size):
            user_id = community[-j - 1]
            user = self.user_getter.get_user_by_id(user_id)
            avg_followers_small += user.followers_count
            avg_friends += user.friends_count
            avg_tweets += user.statuses_count
        avg_followers_large = avg_followers_large / top_size
        avg_followers_small = avg_followers_small / top_size
        avg_friends = avg_friends / top_size
        avg_tweets = avg_tweets / top_size

        log.info("Top " + str(top_size) +
                 " users average number of follower is " +
                 str(avg_followers_large))

        log.info("Bottom " + str(top_size) +
                 " users average number of follower is " +
                 str(avg_followers_small))

        log.info("Bottom " + str(top_size) +
                 " users average number of friends is " +
                 str(avg_friends))

        log.info("Bottom " + str(top_size) +
                 " users average number of tweets is " +
                 str(avg_tweets))

        threshold_followers_large = avg_followers_large * large_account_threshold
        log.info("Candidate number of follower must be at most " +
                 str(threshold_followers_large))

        threshold_followers_small = avg_followers_small * low_account_threshold
        log.info("Candidate number of follower must be at least " +
                 str(threshold_followers_small))

        threshold_friends = avg_friends * friends_threshold
        log.info("Candidate number of friends must be at least " +
                 str(threshold_friends))

        threshold_tweets = avg_tweets * tweet_threshold
        log.info("Candidate number of tweets must be at least " +
                 str(threshold_tweets))

        filtered_candidates = []
        for candidate in candidates:
            curr_candidate = self.user_getter.get_user_by_id(candidate)
            if (curr_candidate is not None and
                    threshold_followers_small < curr_candidate.followers_count < threshold_followers_large and
                    curr_candidate.friends_count > threshold_friends and
                    curr_candidate.statuses_count > threshold_tweets):
                filtered_candidates.append(candidate)

        # log.info(
        #     "Candidates after follower/following/tweets filtering: " + str(filtered_candidates))
        log.info("Candidate list length after follower/following/tweets filtering: " + str(
            len(filtered_candidates)))

        return filtered_candidates

    def filter_candidates_round2(self, candidates, community, threshold_round2):
        """
        Do a second round of candidate filtering where the candidates are ranked based on the number users they follow
        in the community.
        """
        in_common_dict = {}
        for candidate in candidates:
            candidate_friends = self.user_friend_getter.get_user_friends_ids(candidate)
            in_common = len([friend for friend in candidate_friends if friend in community])
            if in_common > 0:
                if in_common not in in_common_dict:
                    in_common_dict[in_common] = []
                in_common_dict[in_common].append(candidate)

        filtered_candidates = []
        in_common_dict = dict(sorted(in_common_dict.items(), reverse=True))

        for count in in_common_dict:
            if count < round(len(community) * threshold_round2):
                break
            users = in_common_dict[count]
            log.info("round 2 filtering: " + str(count) + " friends in community for " + str(
                len(users)) + " users")
            filtered_candidates.extend(users)

        log.info("Candidate list length after  round 2 filtering: " + str(
            len(filtered_candidates)))
        return filtered_candidates

    def filter_candidates_round3(self, candidates, core_users):
        """
        Do a third round of candidate filtering where the candidates set (that also contains the community users)
        is clustered and the cluster with the closest overlap with the core users is selected.
        """
        start_thresh = calculate_threshold_friends(self.user_friend_getter, candidates, top_num=len(candidates), thresh_multiplier=0.1)
        social_graph = construct_social_graph_friends(self.user_friend_getter, candidates, start_thresh)
        increment = start_thresh / 3
        end_thresh = start_thresh + increment * 3
        root_clusters = cluster_social_graph(self.user_friend_getter, social_graph, start_thresh, end_thresh, increment, level_one=True)
        clusters = get_all_clusters(root_clusters)

        selected_cluster = select_cluster(clusters, core_users)

        selected_cluster_users = []
        for u in selected_cluster:
            user_name = self.user_getter.get_user_by_id(u).screen_name
            selected_cluster_users.append(user_name)

        print('selected cluster users: ', selected_cluster_users)

        log.info("Candidate list length after  round 3 filtering: " + str(
            len(selected_cluster)))
        return selected_cluster

    def filter_candidates_round4(self, candidates, community, retweeted_users_threshold):
        """
        Rank the filtered candidates users based on overlap of their retweeted users with the community.
        Remove the cores and the community from the selected cluster.
        Discard the candidates with a score less than threshold.
        """
        scores = {}
        for cand in candidates:
            retweeted_users = list(set(self.retweeted_users_getter.get_retweet_users_ids(cand)))
            if cand in retweeted_users:
                retweeted_users.remove(cand)  # omit self-retweets
            score = jaccard_similarity(retweeted_users, community)
            if score != 0:
                scores[cand] = score

        sorted_candidates = sorted(scores, key=lambda x: scores[x], reverse=True)
        top_size = 10 if len(sorted_candidates) >= 10 else len(sorted_candidates)
        avg_retweeted_users = 0
        for i in range(top_size):
            cand_id = sorted_candidates[i]
            cand_score = scores[cand_id]
            avg_retweeted_users += cand_score
        avg_retweeted_users /= top_size

        new_candidates = []
        for cand in sorted_candidates:
            if cand not in community:
                new_candidates.append(cand)

        log.info("New Candidate list length after  round 3 filtering: " + str(len(new_candidates)))

        log.info(
            "The top " + str(top_size) + " users average number of common retweeted users with the community is " + str(avg_retweeted_users))
        thresh = avg_retweeted_users * retweeted_users_threshold
        log.info("Candidate's number of common retweeted users with the community must be no less than " +
                 str(thresh))

        # discard the candidates with a score less than threshold
        final_filtered_candidates = []
        for cand in new_candidates:
            if scores[cand] >= thresh:
                final_filtered_candidates.append(cand)

        log.info("Discarded " +
                 str(len(new_candidates) - len(final_filtered_candidates))
                 + " candidates in getting the final filtered candidates since they had a low common retweeted users "
                   "with the community")

        log.info("Candidate list length after round 4 filtering: " + str(
            len(final_filtered_candidates)))
        return final_filtered_candidates

    def get_final_candidates(self, final_candidates, core_users):
        """Rank the final filtered candidates users based on social support score w.r.t core users.
        Return the top-10 users"""
        sosu_ranker_scores = self.community_social_support_ranker.score_users(final_candidates, core_users)
        final_candidates = list(
            sorted(sosu_ranker_scores, key=sosu_ranker_scores.get,
                   reverse=True))

        # return the top-10 users
        return final_candidates[:10]

    def expand_community(self, top_size, potential_candidates_size, threshold_round2,
                         follower_threshold, large_account_threshold, low_account_threshold, friends_threshold,
                         tweets_threshold, retweeted_users_threshold,
                         community):
        """Adding candidates until no more is added"""
        track_users_list = community.copy()
        iteration = 0
        prev_community = []
        prev_community_size = 0
        more_potential_candidate = True
        initial_list = community.copy()

        self.write_setup_community_expansion(top_size, potential_candidates_size,
                                             threshold_round2, follower_threshold, large_account_threshold,
                                             low_account_threshold, friends_threshold, tweets_threshold, retweeted_users_threshold)

        # When no available candidate
        while prev_community_size != len(community) or more_potential_candidate:
            if len(community) > 200:
                break
            # if no candidate is added, but there is more candidate available
            if prev_community_size == len(community) and \
                    more_potential_candidate:
                potential_candidates_size += 200

            prev_community_size = len(community)
            community_scores = self.community_social_support_ranker.score_users(community, initial_list)
            community = sorted(community_scores, key=lambda x: community_scores[x], reverse=True)
            # self.dataset_creator.write_dataset(
            #     "expansion", iteration, community, initial_list, prev_community)

            log.info("Iteration: " + str(iteration))
            log.info("Current community size: " + str(len(community)))
            # log.info("Current Community: " + str(community))
            potential_candidate, more_potential_candidate = \
                self.find_potential_candidate(community,
                                              potential_candidates_size,
                                              follower_threshold)

            log.info("Potential candidate list length: " + str(len(potential_candidate)))
            # log.info("Potential candidate list: \n" + str(curr_candidate))

            community_core_users = community[:20]
            # Fist round of filtering candidates
            filtered_candidate = self.filter_candidates_round1(top_size,
                                                               large_account_threshold,
                                                               low_account_threshold,
                                                               friends_threshold,
                                                               tweets_threshold,
                                                               community,
                                                               potential_candidate)

            # Second round of filtering candidates
            filtered_candidate = self.filter_candidates_round2(filtered_candidate, community,
                                                               threshold_round2)

            # Third round of filtering candidates
            filtered_candidate = self.filter_candidates_round3(filtered_candidate, community_core_users)

            # Fourth round of filtering candidates
            filtered_candidate = self.filter_candidates_round4(filtered_candidate, community, retweeted_users_threshold)

            final_candidates = self.get_final_candidates(filtered_candidate, community_core_users)

            log.info("Final Candidate List Length(Fixed): " + str(
                len(final_candidates)))
            # log.info("Final Candidate : " + str(final_candidates))
            new_community = list(
                set(map(str, community + list(final_candidates))))
            prev_community = community
            community = new_community
            iteration = iteration + 1
            track_users_list += final_candidates

        log.info("COMPLETE: No more users to add to the expanded community.")

        community_scores = self.community_social_support_ranker.score_users(community, community)
        community = sorted(community_scores, key=lambda x: community_scores[x], reverse=True)
        self.dataset_creator.write_dataset("final_expansion_sorted", -1, community, community, prev_community)

        self.dataset_creator.write_dataset("final_expansion_unsorted", -1, track_users_list, track_users_list,
                                           prev_community)

        graph_plots(self.initial_seed, track_users_list, self.community_social_support_ranker)
        return community

    def write_setup_community_expansion(self, top_size, potential_candidates_size,
                                        threshold_round2, follower_threshold, large_account_threshold,
                                        low_account_threshold, friends_threshold, tweets_threshold, retweeted_users_threshold):
        data = [
            ['top_size', 'potential_candidates_size', 'threshold_round2',
             'follower_threshold'
             'large_account_threshold',
             'low_account_threshold', 'friends_threshold', 'tweets_threshold', 'retweeted_users_threshold'],
            [top_size, potential_candidates_size,
             threshold_round2, follower_threshold, large_account_threshold,
             low_account_threshold, friends_threshold, tweets_threshold, retweeted_users_threshold]
        ]

        # Open a new CSV file in write mode
        path = str(get_project_root()) + "/data/expansion/" + self.initial_seed + "/community_expansion_setup.csv"
        with open(path, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)

            # Write the data to the file row by row
            for row in data:
                writer.writerow(row)
        file.close()

        log.info('Setup written to community_expansion_setup.csv successfully!')
