from src.process.community_expansion.community_expansion import \
    CommunityExpansionAlgorithm
from src.process.community_expansion.download_helpers import download_user_info_and_tweets, download_friends
from src.shared.logger_factory import LoggerFactory
from src.shared.utils import get_project_root
import csv

log = LoggerFactory.logger(__name__)


def _is_same_list(list1, list2):
    for user1 in list1:
        ret = False
        for user2 in list2:
            if user1 == user2:
                ret = True
        if not ret:
            return ret
    return True


class CoreRefiner(CommunityExpansionAlgorithm):
    """Used to refine initial community, which we assume are a list of core
    users.
    By refining core before expansion, we expect a better result in community
    expansion.
    Refinement stops when no core user changed
    """

    def write_setup_core_refiner(self, top_size, core_size, potential_candidates_size, candidates_size_round1,
                                 candidates_size_round2, follower_threshold, large_account_threshold,
                                 low_account_threshold, friends_threshold, tweets_threshold, sosu_threshold):
        data = [
            ['top_size', 'core_size', 'potential_candidates_size', 'candidates_size_round1', 'candidates_size_round2',
             'follower_threshold'
             'large_account_threshold',
             'low_account_threshold', 'friends_threshold', 'tweets_threshold', 'sosu_threshold'],
            [top_size, core_size, potential_candidates_size, candidates_size_round1,
             candidates_size_round2, follower_threshold, large_account_threshold,
             low_account_threshold, friends_threshold, tweets_threshold, sosu_threshold]
        ]

        # Open a new CSV file in write mode
        path = str(get_project_root()) + "/data/community_expansion/core_refiner_setup.csv"
        with open(path, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)

            # Write the data to the file row by row
            for row in data:
                writer.writerow(row)
        file.close()

        log.info('Setup written to core_refiner_setup.csv successfully!')

    def refine_core(self, top_size, core_size, potential_candidates_size, candidates_size_round1,
                    candidates_size_round2,
                    follower_threshold, large_account_threshold, low_account_threshold, friends_threshold,
                    tweets_threshold, sosu_threshold,
                    community) -> list:

        self.write_setup_core_refiner(top_size, core_size, potential_candidates_size, candidates_size_round1,
                                      candidates_size_round2, follower_threshold, large_account_threshold,
                                      low_account_threshold, friends_threshold, tweets_threshold, sosu_threshold)
        download_user_info_and_tweets(community)
        initial_list = community.copy()
        iteration = 0
        prev_community = initial_list.copy()
        more_potential_candidate = True

        while iteration < 10:
            community_scores = self.community_social_support_ranker.score_users(community, prev_community)
            community = sorted(community_scores, key=lambda x: community_scores[x], reverse=True)
            log.info("Initial list: " + str(len(initial_list)) + str(initial_list))
            log.info("Prev Community: " + str(len(prev_community)) + str(prev_community))
            # Only take top core_size users
            if len(community) > core_size:
                community = community[:core_size]
                community_scores = self.community_social_support_ranker.score_users(community, prev_community)
                community = sorted(community_scores, key=lambda x: community_scores[x], reverse=True)
            self.dataset_creator.write_dataset(
                "core_refine",
                iteration, community, prev_community, prev_community)

            if _is_same_list(community, prev_community):
                if not more_potential_candidate:
                    log.info("more_potential_candidate: " + str(more_potential_candidate))
                    break
                else:
                    potential_candidates_size += 200
            log.info("Core Refine Iteration: " + str(iteration))
            log.info("Current community size: " + str(len(community)))
            log.info("Current Community: " + str(community))
            potential_candidate, more_potential_candidate = \
                self.find_potential_candidate(community,
                                              potential_candidates_size,
                                              follower_threshold)
            log.info("Download candidate and friends")
            curr_candidate = download_user_info_and_tweets(potential_candidate)
            download_friends(curr_candidate)

            log.info("Potential candidate list length: " + str(len(curr_candidate)))
            log.info("Potential candidate list: \n" + str(curr_candidate))
            filtered_candidate = self.filter_candidates_round1(top_size, candidates_size_round1,
                                                               large_account_threshold,
                                                               low_account_threshold,
                                                               friends_threshold,
                                                               tweets_threshold,
                                                               community,
                                                               curr_candidate)
            filtered_candidate = self.filter_candidates_round2(filtered_candidate, community, candidates_size_round2)
            filtered_candidate = self.filter_candidates_round3(filtered_candidate, community,
                                                               self.community_social_support_ranker, top_size)

            final_candidates = self.get_final_candidates(filtered_candidate, community, top_size, sosu_threshold)

            log.info("Final Candidate List Length(Fixed): " + str(len(final_candidates)))
            log.info("Final Candidate : " + str(final_candidates))
            user_names = []
            for user in final_candidates:
                user_names.append(self.user_getter.get_user_by_id(user).screen_name)
            log.info("Candidate names: " + str(user_names))
            new_community = list(set(map(str, community + list(final_candidates))))
            prev_community = community
            community = new_community
            iteration = iteration + 1
            log.info("New Community Length:  " + str(len(community)))

        community_scores = self.community_social_support_ranker.score_users(community, community)
        community = sorted(community_scores, key=lambda x: community_scores[x], reverse=True)
        self.dataset_creator.write_dataset("final_core_refine", -1, community, community, prev_community)

        return community
