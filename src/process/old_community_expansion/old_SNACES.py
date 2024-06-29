#!/usr/bin/env python
import click

from src.process.community_ranking.community_influence_one_ranker import CommunityInfluenceOneRanker
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker
from src.process.community_ranking.community_ss_intersection_ranker import CommunitySSIntersectionRanker
from src.process.data_analysis.dataset_creator import DatasetCreator
from src.process.old_community_expansion.old_community_expansion import OldCommunityExpansionAlgorithm
from src.process.old_community_expansion.old_core_refiner import OldCoreRefiner
from src.shared.logger_factory import LoggerFactory
from src.shared.utils import get_project_root
import src.dependencies.injector as sdi

path = str(get_project_root()) + \
       "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
injector = sdi.Injector.get_injector_from_file(path)
process_module = injector.get_process_module()
dao_module = injector.get_dao_module()
log = LoggerFactory.logger(__name__)


# Event handlers

def run_community_expansion():
    click.echo("Community Expansion")
    click.echo("Assume initial users are CORE users. "
               "The cleaner initial users are, the better expansion result.")

    bluesky_getter = dao_module.get_bluesky_getter()
    user_tweets_getter = dao_module.get_user_tweets_getter()
    friends_getter = dao_module.get_user_friend_getter()
    ranking_setter = dao_module.get_ranking_setter()
    user_getter = dao_module.get_user_getter()
    user_downloader = process_module.get_user_downloader()
    user_tweet_downloader = process_module.get_user_tweet_downloader()
    friend_downloader = process_module.get_friend_downloader()

    community_social_support_ranker = CommunitySocialSupportRanker(user_tweets_getter, friends_getter, ranking_setter)
    community_influence1_ranker = CommunityInfluenceOneRanker(user_tweets_getter, friends_getter, ranking_setter)

    # Use social support intersection ranker for core refinement
    ranker_list_core_refiner = [community_influence1_ranker, community_social_support_ranker]
    intersection_ranker_core_refiner = CommunitySSIntersectionRanker(ranker_list_core_refiner)

    # Use social support intersection ranker for community expansion
    ranker_list_expansion = [community_influence1_ranker, community_social_support_ranker]
    intersection_ranker_expansion = CommunitySSIntersectionRanker(ranker_list_expansion)

    initial_user_list = ['katharinehayhoe.com', 'edhawkins.bsky.social', 'indianaclimate.bsky.social',
                         'peterthorne.bsky.social', 'meadekrosby.bsky.social', 'zlabe.bsky.social',
                         'micefearboggis.bsky.social', 'mathewabarlow.bsky.social', 'irishrainforest.bsky.social',
                         'seismatters.bsky.social']
    # get user ids of the users in initial_user_list
    initial_user_list2 = []
    for initial_user in initial_user_list:
        initial_user_list2.append(bluesky_getter.get_user_by_screen_name(initial_user).id)
    initial_user_list = initial_user_list2

    file_path = str(get_project_root()) + "/data/old_community_expansion/"

    dataset_creator_core_refiner = DatasetCreator(
        file_path,
        user_getter,
        user_downloader,
        user_tweets_getter,
        user_tweet_downloader,
        friends_getter,
        friend_downloader,
        ranker_list_core_refiner)

    dataset_creator_expansion = DatasetCreator(
        file_path,
        user_getter,
        user_downloader,
        user_tweets_getter,
        user_tweet_downloader,
        friends_getter,
        friend_downloader,
        ranker_list_expansion)

    core_refiner = OldCoreRefiner(user_getter,
                                  user_downloader,
                                  user_tweets_getter,
                                  user_tweet_downloader,
                                  friends_getter,
                                  friend_downloader,
                                  ranker_list_core_refiner,
                                  intersection_ranker_core_refiner,
                                  dataset_creator_core_refiner)

    initial_user_list = core_refiner.refine_core(
        threshold=0.025, top_size=5, candidates_size=20, large_account_threshold=1.5, low_account_threshold=0.5,
        follower_threshold=0.5, core_size=20, num_of_candidate=200, community=initial_user_list, mode=False)

    algorithm = OldCommunityExpansionAlgorithm(
        user_getter,
        user_downloader,
        user_tweets_getter,
        user_tweet_downloader,
        friends_getter,
        friend_downloader,
        ranker_list_expansion,
        intersection_ranker_expansion,
        dataset_creator_expansion)

    # Since we are doing a second-round candidate filtering in community expansion algorithm, we relax the thresholds
    # and increase candidates size
    algorithm.expand_community(
        threshold=0.025, top_size=10, candidates_size=30,
        large_account_threshold=2.0, low_account_threshold=0.25, follower_threshold=0.2,
        num_of_candidate=500, community=initial_user_list, mode=True)


@click.command()
def main():
    click.echo("====================================================")
    click.echo("                       SNACES                       ")
    click.echo("Social Network Algorithm Contained Experiment System")
    click.echo("====================================================")
    click.echo("Processes:")
    click.echo("1. Community Expansion")

    val = click.prompt("Choose a process")
    if int(val) == 1:
        run_community_expansion()
    else:
        raise Exception("Invalid input")


if __name__ == "__main__":
    main()
