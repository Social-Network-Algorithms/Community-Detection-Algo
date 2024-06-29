from src.process.old_community_expansion.old_community_expansion import OldCommunityExpansionAlgorithm
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


class OldCoreRefiner(OldCommunityExpansionAlgorithm):
    """Used to refine initial community, which we assume are a list of core
    users.
    By refining core before expansion, we expect a better result in community
    expansion.
    Refinement stops when no core user changed
    """

    def write_setup_core_refiner(self, threshold, top_size, candidates_size,
                                 large_account_threshold, low_account_threshold, follower_threshold,
                                 core_size, num_of_candidate):
        data = [
            ['threshold', 'top_size', 'candidates_size', 'large_account_threshold', 'low_account_threshold',
             'follower_threshold', 'core_size', 'num_of_candidate'],
            [threshold, top_size, candidates_size, large_account_threshold, low_account_threshold,
             follower_threshold, core_size, num_of_candidate]
        ]

        # Open a new CSV file in write mode
        path = str(get_project_root()) + "/data/old_community_expansion/core_refiner_setup.csv"
        with open(path, mode='w', newline='') as file:
            # Create a CSV writer object
            writer = csv.writer(file)

            # Write the data to the file row by row
            for row in data:
                writer.writerow(row)
        file.close()

        log.info('Setup written to core_refiner_setup.csv successfully!')

    def refine_core(self, threshold, top_size, candidates_size,
                    large_account_threshold, low_account_threshold, follower_threshold,
                    core_size, num_of_candidate, community, mode) -> list:

        self.write_setup_core_refiner(threshold, top_size, candidates_size, large_account_threshold,
                                      low_account_threshold, follower_threshold, core_size, num_of_candidate)
        self.download_user_info_and_tweets(community)
        initial_list = community.copy()
        iteration = 0
        prev_community = initial_list.copy()
        more_potential_candidate = True

        while iteration < 10:
            community, _ = self.intersection_ranker.rank(community, prev_community, mode)
            log.info("Initial list: " + str(len(initial_list)) + str(initial_list))
            log.info("Prev Community: " + str(len(prev_community)) + str(prev_community))
            # Only take top core_size users
            if len(community) > core_size:
                community = community[:core_size]
                community, _ = self.intersection_ranker.rank(community, prev_community, mode)
            # self.dataset_creator.write_dataset(
            #     "core_refine",
            #     iteration, community, prev_community, prev_community)
            if _is_same_list(community, prev_community):
                if not more_potential_candidate:
                    log.info("more_potential_candidate: " + str(more_potential_candidate))
                    break
                else:
                    num_of_candidate += 200
            log.info("Core Refine Iteration: " + str(iteration))
            log.info("Current community size: " + str(len(community)))
            log.info("Current Community: " + str(community))
            # self.download_friends(community)
            potential_candidate, more_potential_candidate = \
                self.find_potential_candidate(community,
                                              num_of_candidate,
                                              follower_threshold)
            log.info("Download candidate and friends")
            curr_candidate = self.download_user_info_and_tweets(potential_candidate)
            self.download_friends(curr_candidate)

            log.info("Potential candidate list length: " + str(len(curr_candidate)))
            log.info("Potential candidate list: \n" + str(curr_candidate))
            filtered_candidate = self.filter_candidates_round1(threshold, top_size,
                                                               candidates_size, large_account_threshold,
                                                               low_account_threshold,
                                                               community, prev_community, curr_candidate, mode)
            log.info("Final Candidate List Length(Fixed): " + str(len(filtered_candidate)))
            log.info("Final Candidate : " + str(filtered_candidate))
            user_names = []
            for user in filtered_candidate:
                user_names.append(self.user_getter.get_user_by_id(user).screen_name)
            log.info("Candidate names: " + str(user_names))
            new_community = list(set(map(str, community + list(filtered_candidate))))
            prev_community = community
            community = new_community
            iteration = iteration + 1
            log.info("New Community Length:  " + str(len(community)))

        community, community_scores = self.intersection_ranker.rank(community, community, mode)
        self.dataset_creator.write_dataset("final_core_refine", -1, community, community, prev_community)

        return community
