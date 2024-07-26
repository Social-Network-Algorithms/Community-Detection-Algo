from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter

from src.process.community_expansion.clustering_helper import *
from src.process.community_expansion.download_helpers import download_user_info_and_tweets
from src.process.community_expansion.plotting_helper import graph_plots
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
import csv

log = LoggerFactory.logger(__name__)
DEFAULT_PATH = str(
    get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


class CommunityExpansionAlgorithm:
    def __init__(self, user_getter,
                 user_tweets_getter: UserTweetsGetter,
                 user_friend_getter,
                 dataset_creator):
        self.user_getter = user_getter
        self.user_friend_getter = user_friend_getter
        self.dataset_creator = dataset_creator
        self.community_social_support_ranker = CommunitySocialSupportRanker(user_tweets_getter, user_friend_getter,
                                                                            None)

    def find_potential_candidate(self, users, num_of_candidate, threshold):
        """
        Find potential candidates from users' followings in current community.
        """
        # user_map: key: candidate, value: number of follower in community
        user_map = {}
        for user_id in users:
            user_friends = self.user_friend_getter.get_user_friends_ids(user_id)
            for candidate in user_friends:
                if candidate not in users:
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
        log.info("want candidate have at least" + str(threshold_1) +
                 "followers in the community")

        candidate = []
        # whether or not there are more potential candidate than we asked for
        more_potential_candidate = True
        for i in range(len(users), -1, -1):
            if i in result:
                if len(result[i]) + len(candidate) <= num_of_candidate and \
                        i >= threshold_1:
                    log.info(str(len(result[i])) + " candidates has " + str(i) +
                             " common followers in current cluster")

                    candidate.extend(result[i])
                else:
                    if i < threshold_1:
                        log.info(
                            "break because common user reaches the minimum")
                        more_potential_candidate = False
                    break
        return candidate, more_potential_candidate

    def filter_candidates_round1(self, top_size, candidates_size,
                                 large_account_threshold, low_account_threshold, friends_threshold, tweet_threshold,
                                 community, candidates):
        """
        top_size: Top <top_size> users are used for measurement
        candidates_size: Only keep <candidates_size> users from the potential candidates
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
        if top_size > len(community):
            top_size = len(community)
        if top_size < int(len(community) / 3):
            top_size = int(len(community) / 3)

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

        num_users = len(candidates)
        filtered_candidates = candidates
        while num_users > candidates_size:
            num_users = len(candidates)
            filtered_candidates = []
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

            for candidate in candidates:
                num_users -= 1
                curr_candidate = self.user_getter.get_user_by_id(candidate)
                if (threshold_followers_small < curr_candidate.followers_count < threshold_followers_large and
                        curr_candidate.friends_count > threshold_friends and
                        curr_candidate.statuses_count > threshold_tweets):
                    filtered_candidates.append(candidate)
                    num_users += 1

            log.info(
                f"Increasing Data Cleaning Strength, {num_users} remaining users")
            large_account_threshold -= 0.02
            low_account_threshold += 0.02
            friends_threshold += 0.02
            tweet_threshold += 0.02

        # log.info(
        #     "Candidates after follower/following/tweets filtering: " + str(filtered_candidates))
        log.info("Candidate list length after follower/following/tweets filtering: " + str(
            len(filtered_candidates)))

        return filtered_candidates

    def filter_candidates_round2(self, candidates, community, candidates_size):
        """
        Do a second round of candidate filtering where the candidates are ranked based on the number of their friends
        in the current community. The top <candidates_size> users are returned.
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
            users = in_common_dict[count]
            log.info("round 2 filtering: " + str(count) + " in common friends with community for " + str(len(users)) + " users")
            if len(users) + len(filtered_candidates) > candidates_size:
                filtered_candidates.extend(users[:(candidates_size - len(filtered_candidates))])
                break
            else:
                filtered_candidates.extend(users)

        # log.info(
        #     "Candidates after round 2 filtering: " + str(filtered_candidates))
        log.info("Candidate list length after  round 2 filtering: " + str(
            len(filtered_candidates)))
        return filtered_candidates

    def filter_candidates_round3(self, candidates, current_community, sosu_ranker, top_size):
        """
        Do a third round of candidate filtering where the candidates set is clustered and the cluster with the
        closest relationship to the core users is selected.
        The users in this cluster are the final filtered candidates.
        """
        start_thresh, end_thresh, increment = 0.0001, 0.001, 0.0003
        social_graph = construct_social_graph(candidates, start_thresh)
        clusters = cluster_social_graph(social_graph, start_thresh, end_thresh, increment, top_size)
        selected_cluster = select_cluster(clusters, current_community, sosu_ranker, top_size)
        # log.info(
        #     "Candidates after round 3 filtering: " + str(selected_cluster))
        log.info("Candidate list length after  round 3 filtering: " + str(
            len(selected_cluster)))
        return selected_cluster

    def get_final_candidates(self, candidates, current_community, top_size, sosu_threshold):
        """Rank the final filtered candidates users based on their social support score with respect to the core users.
        Discard the ones with a score less than <sosu_threshold>% ranking score of the average of top <top_size> users.
        The top-10 remaining users are the final candidates and will be added to the community."""
        top_users = current_community[:top_size]
        top_users_sosu_ranker_scores = self.community_social_support_ranker.score_users(top_users, current_community)
        avg_sosu_ranking = sum(top_users_sosu_ranker_scores.values()) / top_size
        log.info("Top " + str(top_size) +
                 " users average number of social support is " +
                 str(avg_sosu_ranking))

        threshold_sosu = sosu_threshold * avg_sosu_ranking
        log.info("Candidate social support ranker score must be no less than " +
                 str(threshold_sosu))

        candidates_sosu_ranker_scores = self.community_social_support_ranker.score_users(candidates, current_community)
        # discard the candidates with a score less than threshold_sosu
        filtered_candidates_sosu_ranker_scores = {}
        for user in candidates_sosu_ranker_scores:
            user_score = candidates_sosu_ranker_scores[user]
            if user_score > threshold_sosu:
                filtered_candidates_sosu_ranker_scores[user] = user_score

        log.info("Discarded " +
                 str(len(candidates_sosu_ranker_scores.keys()) - len(filtered_candidates_sosu_ranker_scores.keys()))
                 + " candidates in getting the final candidates since they had a small sosu score w.r.t. community ")

        # sort the filtered candidates based on their scores
        sorted_candidates = sorted(filtered_candidates_sosu_ranker_scores,
                                   key=lambda x: filtered_candidates_sosu_ranker_scores[x], reverse=True)
        # return the top-10 users
        return sorted_candidates[:10]

    def expand_community(self, top_size, potential_candidates_size, candidates_size_round1, candidates_size_round2,
                         follower_threshold, large_account_threshold, low_account_threshold, friends_threshold,
                         tweets_threshold, sosu_threshold,
                         community):
        """Adding candidates until no more is added"""
        track_users_list = community.copy()
        iteration = 0
        prev_community = []
        prev_community_size = 0
        more_potential_candidate = True
        download_user_info_and_tweets(community)
        initial_list = community.copy()

        self.write_setup_community_expansion(top_size, potential_candidates_size, candidates_size_round1,
                                             candidates_size_round2, follower_threshold, large_account_threshold,
                                             low_account_threshold, friends_threshold, tweets_threshold, sosu_threshold)

        # When no available candidate
        while prev_community_size != len(community) or more_potential_candidate:
            if len(community) > 500:
                break
            # if no candidate is added, but there is more candidate available
            if prev_community_size == len(community) and \
                    more_potential_candidate:
                potential_candidates_size += 200

            prev_community_size = len(community)
            community_scores = self.community_social_support_ranker.score_users(community, initial_list)
            community = sorted(community_scores, key=lambda x: community_scores[x], reverse=True)
            self.dataset_creator.write_dataset(
                "expansion", iteration, community, initial_list, prev_community)

            log.info("Iteration: " + str(iteration))
            log.info("Current community size: " + str(len(community)))
            # log.info("Current Community: " + str(community))
            potential_candidate, more_potential_candidate = \
                self.find_potential_candidate(community,
                                              potential_candidates_size,
                                              follower_threshold)
            # log.info("Download candidate and friends")
            curr_candidate = download_user_info_and_tweets(potential_candidate)

            log.info("Potential candidate list length: " + str(len(curr_candidate)))
            # log.info("Potential candidate list: \n" + str(curr_candidate))
            # Fist round of filtering candidates
            filtered_candidate = self.filter_candidates_round1(top_size, candidates_size_round1,
                                                               large_account_threshold,
                                                               low_account_threshold,
                                                               friends_threshold,
                                                               tweets_threshold,
                                                               community,
                                                               curr_candidate)
            # Second round of filtering candidates
            filtered_candidate = self.filter_candidates_round2(filtered_candidate, community, candidates_size_round2)

            # Third round of filtering candidates
            filtered_candidate = self.filter_candidates_round3(filtered_candidate, initial_list,
                                                               self.community_social_support_ranker, top_size)

            final_candidates = self.get_final_candidates(filtered_candidate, initial_list, top_size, sosu_threshold)

            log.info("Final Candidate List Length(Fixed): " + str(
                len(final_candidates)))
            log.info("Final Candidate : " + str(final_candidates))
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

        graph_plots(track_users_list)

    def write_setup_community_expansion(self, top_size, potential_candidates_size, candidates_size_round1,
                                        candidates_size_round2, follower_threshold, large_account_threshold,
                                        low_account_threshold, friends_threshold, tweets_threshold, sosu_threshold):
        data = [
            ['top_size', 'potential_candidates_size', 'candidates_size_round1', 'candidates_size_round2',
             'follower_threshold'
             'large_account_threshold',
             'low_account_threshold', 'friends_threshold', 'tweets_threshold', 'sosu_threshold'],
            [top_size, potential_candidates_size, candidates_size_round1,
             candidates_size_round2, follower_threshold, large_account_threshold,
             low_account_threshold, friends_threshold, tweets_threshold, sosu_threshold]
        ]

        # Open a new CSV file in write mode
        path = str(get_project_root()) + "/data/community_expansion/community_expansion_setup.csv"
        with open(path, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)

            # Write the data to the file row by row
            for row in data:
                writer.writerow(row)
        file.close()

        log.info('Setup written to community_expansion_setup.csv successfully!')
