from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.process.community_ranking.community_intersection_ranker import CommunityIntersectionRanker
from src.process.community_ranking.community_ss_intersection_ranker import CommunitySSIntersectionRanker
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
import csv

log = LoggerFactory.logger(__name__)
DEFAULT_PATH = str(
    get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


class CommunityExpansionAlgorithm:
    def __init__(self, user_getter, user_downloader,
                 user_tweets_getter: UserTweetsGetter, user_tweet_downloader,
                 user_friend_getter, user_friends_downloader,
                 ranker_list, dataset_creator):
        self.user_getter = user_getter
        self.user_downloader = user_downloader
        self.user_tweets_getter = user_tweets_getter
        self.user_tweet_downloader = user_tweet_downloader
        self.user_friend_getter = user_friend_getter
        self.user_friends_downloader = user_friends_downloader
        self.ranker_list = ranker_list
        # Uncomment if using Social Support
        self.intersection_ranker = CommunitySSIntersectionRanker(self.ranker_list)
        # self.intersection_ranker = CommunityIntersectionRanker(self.ranker_list)
        self.dataset_creator = dataset_creator

    def download_friends(self, curr_candidates):
        for curr_candidate in curr_candidates:
            friend_list = self.user_friend_getter.get_user_friends_ids(curr_candidate)
            if friend_list is None:
                log.info("Download friends of " + str(curr_candidate))
                self.user_friends_downloader.download_friends_ids_by_id(curr_candidate)

    def download_user_info_and_tweets(self, curr_candidates):
        user_ids = []
        for curr_candidate in curr_candidates:
            user_info = self.user_getter.get_user_by_id(curr_candidate)
            user_id = None
            if user_info is None:
                try:
                    log.info("Download user " + str(curr_candidate))
                    self.user_downloader.download_user_by_id(curr_candidate)
                    user_info = self.user_getter.get_user_by_id(curr_candidate)
                    user_id = user_info.id
                except:
                    log.info("[Download Error] Cannot download user " + str(curr_candidate))
            else:
                user_id = user_info.id

            if user_id is not None:
                tweets_list = self.user_tweets_getter.get_user_tweets(user_id)
                if tweets_list is None:
                    log.info("Download tweets of " + str(user_id))
                    self.user_tweet_downloader.download_user_tweets_by_user_id(user_id)

                user_ids.append(user_id)

        return user_ids


    def filter_candidates(self, threshold, top_size, candidates_size,
                          large_account_threshold, low_account_threshold,
                          community, respection, candidates, mode):
        """
        threshold: candidate must have utility more than <threshold>% of
            average utility of top <top_size> users.
        top_size: Top <top_size> users are used for measurement
        candidates_size: Only keep <candidates_size> user
            by their intersection rank.
        large_account_threshold: If no restriction on large account,
            large_account_threshold = -1. Otherwise, candidate cannot have
            more than <large_account_threshold>% number of followers than
            average of top <top_size> users.
        """
        if top_size > len(community):
            top_size = len(community)
        if top_size < int(len(community) / 3):
            top_size = int(len(community) / 3)

        # community = self.intersection_ranker.rank(community, respection)

        log.info("Candidate utilities higher than " +
                 str(threshold) + " of average of top " + str(top_size) +
                 " users in the community.")
        # Calculate threshold for each utility
        thresholds = []

        # Uncomment if Social Support
        ranker_scores = []
        for i in range(len(self.ranker_list)):
            ranker_scores.append(self.ranker_list[i].score_users(community, respection))

        for i in range(len(self.ranker_list)):
            thresholds.append(0)
            for j in range(top_size):
                user = community[j]
                thresholds[i] += ranker_scores[i][user]
                # thresholds[i] += self.ranker_list[i].score_user(user, respection)
            thresholds[i] = thresholds[i] / float(top_size)
            log.info("Top " + str(top_size) + " users average " +
                     self.ranker_list[i].ranking_function_name + " is " +
                     str(thresholds[i]))
            thresholds[i] = thresholds[i] * threshold
            log.info("Candidate " + self.ranker_list[i].ranking_function_name +
                     " must be no less than " + str(thresholds[i]))

        threshold_followers_1 = 0
        threshold_followers_2 = 0
        threshold_followers_large = 0
        threshold_followers_small = 0
        # If filter user with large size of followers:
        if large_account_threshold != -1:
            for j in range(top_size):
                user_id = community[j]
                user = self.user_getter.get_user_by_id(user_id)
                threshold_followers_1 += user.followers_count
            for j in range(top_size):
                user_id = community[-j-1]
                user = self.user_getter.get_user_by_id(user_id)
                threshold_followers_2 += user.followers_count
            threshold_followers_1 = threshold_followers_1 / top_size
            threshold_followers_2 = threshold_followers_2 / top_size

            log.info("Top " + str(top_size) +
                     " users average number of follower is " +
                     str(threshold_followers_1))
            threshold_followers_large = threshold_followers_1 * large_account_threshold
            log.info("Candidate number of follower must be no more than " +
                     str(threshold_followers_large))

            log.info("Bottom " + str(top_size) +
                     " users average number of follower is " +
                     str(threshold_followers_2))
            threshold_followers_small = threshold_followers_2 * low_account_threshold
            log.info("Candidate number of follower must be no less than " +
                     str(threshold_followers_small))

        # Uncomment if Social Support

        ranker_scores = []
        candidates_str = []
        for candidate in candidates:
            candidates_str.append(str(candidate))
        for i in range(len(self.ranker_list)):
            ranker_scores.append(self.ranker_list[i].score_users(candidates_str, respection))


        filtered_candidates = []
        for candidate in candidates:
            accept = True

            if mode is True:
                # Uncomment if Social Support
                score_influence_1 = ranker_scores[0][str(candidate)]
                score_social_support = ranker_scores[1][str(candidate)]
                if (score_influence_1 >= thresholds[0] and score_social_support >= thresholds[1]):
                    accept = True
                else:
                    accept = False
                '''
                score_influence_1 = self.ranker_list[0].score_user(str(candidate), respection)
                score_influence_2 = self.ranker_list[1].score_user(str(candidate), respection)
                score_production = self.ranker_list[2].score_user(str(candidate), respection)
                score_consumption = self.ranker_list[3].score_user(str(candidate), respection)
                if (score_influence_1 >= thresholds[0] or score_influence_2 >= thresholds[1]) and \
                        score_production >= thresholds[2] and score_consumption >= thresholds[3]:
                    accept = True
                else:
                    accept = False
                '''
            else:
                for i in range(len(self.ranker_list)):
                    # log.info("Calculating ranking " + str(self.ranker_list[i].ranking_function_name))
                    score = self.ranker_list[i].score_user(str(candidate), respection)
                    # log.info("Finish calculation")
                    if score < thresholds[i]:
                        accept = False

                    if str(candidate) in ['609121227', '13247182', '94340676', '228806806']:
                        log.info(str(candidate) + " " + self.ranker_list[i].ranking_function_name + ": " + str(score))

            if large_account_threshold != -1 and \
                    self.user_getter.get_user_by_id(candidate).followers_count > threshold_followers_large:
                accept = False
            if low_account_threshold != -1 and \
                    self.user_getter.get_user_by_id(candidate).followers_count < threshold_followers_small:
                accept = False
            if accept:
                filtered_candidates.append(str(candidate))

            log.info("Filter Candidate " + str(candidate) + ": " + str(accept))

        log.info(
            "Candidates after utility filtering: " + str(filtered_candidates))
        log.info("Candidate list length after utility filtering: " + str(
            len(filtered_candidates)))

        # Take the top <candidate_size> new users by intersection_ranking
        candidate_list = []
        intersection_ranking = \
            self.intersection_ranker.rank(filtered_candidates, respection, mode)
        for user in intersection_ranking:
            if user not in community:
                candidate_list.append(user)
            if len(candidate_list) == candidates_size:
                break
        return candidate_list

    def find_potential_candidate(self, users, num_of_candidate, threshold):
        """
        Find potential candidates from users' followings
        in current community.
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
        # threshold_2 = len(users) * threshold
        # log.info("want candidate follow at least" + str(threshold_2) + "users in the community")
        candidate = []
        # whether or not there are more potential candidate than we asked for
        more_potential_candidate = True
        for i in range(len(users), -1, -1):
            if i in result:
                if len(result[i]) + len(candidate) <= num_of_candidate and \
                        i >= threshold_1:
                    log.info(str(len(result[i])) + " candidates has " + str(i) +
                             "common followers in current cluster")
                    # self._download_friends(result[i])
                    # for user in result[i]:
                    #     if len([x for x in users if str(x) in self.user_friend_getter.get_user_friends_ids(user)]) >= threshold_2:
                    #         candidate.append(user)
                    candidate.extend(result[i])
                else:
                    if i < threshold_1:
                        log.info(
                            "break because common user reaches the minimum")
                        more_potential_candidate = False
                    break
        return candidate, more_potential_candidate

    def write_setup_community_expansion(self, threshold, top_size, candidates_size, large_account_threshold,
                                        low_account_threshold, follower_threshold, num_of_candidate):
        data = [
            ['threshold', 'top_size', 'candidates_size', 'large_account_threshold', 'low_account_threshold'
             'follower_threshold', 'num_of_candidate'],
            [threshold, top_size, candidates_size, large_account_threshold, low_account_threshold,
             follower_threshold, num_of_candidate]
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

    def expand_community(self, threshold, top_size, candidates_size, large_account_threshold, low_account_threshold,
                         follower_threshold, num_of_candidate, community, mode):
        """Adding candidates until no more is added"""
        iteration = 0
        prev_community = []
        prev_community_size = 0
        more_potential_candidate = True
        self.download_user_info_and_tweets(community)
        initial_list = community.copy()

        self.write_setup_community_expansion(threshold, top_size, candidates_size, large_account_threshold,
                                             low_account_threshold, follower_threshold, num_of_candidate)

        # When no available candidate
        while prev_community_size != len(community) or more_potential_candidate:
            # if no candidate is added, but there is more candidate available
            if prev_community_size == len(community) and \
                    more_potential_candidate:
                num_of_candidate += 200

            prev_community_size = len(community)
            community = self.intersection_ranker.rank(community, initial_list, mode)
            self.dataset_creator.write_dataset(
                "expansion", iteration, community, initial_list, prev_community)
            log.info("Iteration: " + str(iteration))
            log.info("Current community size: " + str(len(community)))
            log.info("Current Community: " + str(community))
            self.download_friends(community)
            potential_candidate, more_potential_candidate = \
                self.find_potential_candidate(community,
                                              num_of_candidate,
                                              follower_threshold)
            log.info("Download candidate and friends")
            curr_candidate = self.download_user_info_and_tweets(potential_candidate)
            self.download_friends(curr_candidate)

            log.info("Potential candidate list length: " + str(len(curr_candidate)))
            log.info("Potential candidate list: \n" + str(curr_candidate))
            filtered_candidate = self.filter_candidates(threshold, top_size, candidates_size, large_account_threshold,
                                                        low_account_threshold, community, initial_list, curr_candidate, mode)
            log.info("Final Candidate List Length(Fixed): " + str(
                len(filtered_candidate)))
            log.info("Final Candidate : " + str(filtered_candidate))
            new_community = list(
                set(map(str, community + list(filtered_candidate))))
            prev_community = community
            community = new_community
            iteration = iteration + 1

        community = self.intersection_ranker.rank(community, community, mode)
        self.dataset_creator.write_dataset("final_expansion", -1, community, community, prev_community)