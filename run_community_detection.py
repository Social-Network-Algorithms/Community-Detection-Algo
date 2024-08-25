import argparse
import os

import click

from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
injector = Injector.get_injector_from_file(DEFAULT_PATH)
process_module = injector.get_process_module()
dao_module = injector.get_dao_module()


def get_community(name: str, activity: str):
    try:
        # the results can be seen under the "data/{username}" directory
        data_path = str(get_project_root()) + "/data/expansion/" + name + "/"
        os.makedirs(data_path)
        test_path = str(get_project_root()) + "/data/tests/" + name + "/"
        os.makedirs(test_path)
    except Exception as e:
        pass

    try:
        influential_users, seeds, seed_clusters = detect_influential_users(name, activity)
        community = detect_community(name, influential_users)
        test_community_quality(name, community, seeds, seed_clusters)

    except Exception as e:
        log.exception(e)
        exit()


def detect_influential_users(name: str, activity: str):
    core_detector = process_module.get_jaccard_core_detector(activity)
    influential_users = core_detector.detect_core_by_screen_name(name, activity)
    return influential_users


def detect_community(seed, influential_users):
    click.echo("Community Expansion")
    click.echo("Assume initial users are CORE users. "
               "The cleaner initial users are, the better expansion result.")

    file_path = str(get_project_root()) + "/data/expansion/" + seed + "/"
    dataset_creator = process_module.get_dataset_creator(file_path)
    core_refiner = process_module.get_core_refiner(seed, dataset_creator)
    community_expansion = process_module.get_community_expansion(seed, dataset_creator)

    influential_users = core_refiner.refine_core(
        core_size=20, potential_candidates_size=600, threshold_round2=0.2,
        follower_threshold=0.4, large_account_threshold=5.0, low_account_threshold=0.25, friends_threshold=0.15,
        tweets_threshold=0.15, retweeted_users_threshold=0.5, community=influential_users)

    community = community_expansion.expand_community(
        top_size=20, potential_candidates_size=1200, threshold_round2=0.2,
        follower_threshold=0.2, large_account_threshold=5.0, low_account_threshold=0.25, friends_threshold=0.15,
        tweets_threshold=0.15, retweeted_users_threshold=0.4, community=influential_users)

    return community


def test_community_quality(initial_seed, community, seeds, seed_clusters):
    community_quality_tests = process_module.get_community_quality_tests(initial_seed)
    for test in community_quality_tests:
        test.run_tests(community, seeds, seed_clusters)


if __name__ == "__main__":
    """
    Short script to detect a community
    """
    # act: friends, user retweets, user retweets ids
    parser = argparse.ArgumentParser(description='Detects the community for the given seed user')
    parser.add_argument('-n', '--name', dest='name', required=True,
                        help='The name of the user to start on', type=str)

    args = parser.parse_args()

    get_community(args.name, activity="friends")
