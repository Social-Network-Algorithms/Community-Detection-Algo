#!/usr/bin/env python
import click

from src.shared.logger_factory import LoggerFactory
from src.shared.utils import get_project_root
from src.tools.user_list_processor import UserListProcessor
import src.dependencies.injector as sdi

# Download
import src.tools.download_daemon as download_daemon
from src.shared.utils import get_date
from src.process.download.bluesky_downloader import BlueskyTweetDownloader, BlueskyFriendsDownloader, \
    BlueskyFollowersDownloader

# Raw Tweet Processing 
from src.process.raw_tweet_processing.raw_tweet_processor import RawTweetProcessor

# Word Frequency
from src.process.word_frequency.word_frequency import WordFrequency

# Social Graph
from src.process.social_graph.social_graph import SocialGraph

# Affinity Propagation
from src.process.clustering.affinity_propagation.affinity_propagation import AffinityPropagation
from src.process.clustering.affinity_propagation.ap_config_parser import AffinityPropagationConfigParser

# Label Propagation
from src.process.clustering.label_propagation.label_propagation import LabelPropagation
from src.process.clustering.label_propagation.lp_config_parser import LabelPropagationConfigParser

# MUISI
from src.process.clustering.MUISI.standard.muisi import MUISI, MUISIConfig
from src.process.clustering.MUISI.muisi_config_parser import MUISIConfigParser

# MUISI Retweets
from src.process.clustering.MUISI.retweets.muisi_retweet import MUISIRetweet, MUISIRetweetConfig

# Community Expansion
from src.process.community_expansion.community_expansion import CommunityExpansionAlgorithm
from src.process.community_expansion.core_refiner import CoreRefiner
from src.process.data_analysis.dataset_creator import DatasetCreator

path = str(get_project_root()) + \
       "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
injector = sdi.Injector.get_injector_from_file(path)
process_module = injector.get_process_module()
dao_module = injector.get_dao_module()
log = LoggerFactory.logger(__name__)


# CLI Helpers
def get_user():
    ulp = None
    use_user_list = click.confirm("Do you wish to provide a user list?")
    if use_user_list:
        default_ul_path = get_project_root() / 'src' / 'tools' / 'user_list'
        ul_path = click.prompt("User List Path", default_ul_path)
        ulp = UserListProcessor()
        user_or_user_list = ulp.user_list_parser(ul_path)
    else:
        user_or_user_list = click.prompt("User")

    return use_user_list, user_or_user_list, ulp


# Event handlers
def run_download():
    click.echo("Provide the full path the the download config(leave blank to set to default)")
    twitter_getter = dao_module.get_twitter_getter()

    user_friends_getter = dao_module.get_user_friend_getter()
    user_friends_setter = dao_module.get_user_friend_setter()
    user_tweets_setter = dao_module.get_user_tweets_setter()
    user_followers_setter = dao_module.get_user_follower_setter()

    click.echo("Download Types:")
    click.echo("1. Twitter Tweet Download")
    click.echo("2. Twitter Friends Download")
    click.echo("3. Twitter Followers Download")
    download_type = click.prompt("Choose a download type", type=int)

    if download_type == 1:
        tweet_downloader = BlueskyTweetDownloader()
        click.echo("Tweet types:")
        click.echo("1. User Tweets")
        click.echo("2. Random Tweets")
        tweet_type = click.prompt("Choose what to download", type=int)
        if tweet_type == 1:
            click.echo("Downloading User Tweets")
            use_user_list, user_or_user_list, ulp = get_user()
            # num_tweets = click.prompt("Number of Tweets(leave blank to get all)", type=int)
            if click.confirm("Do you want to specify a start and end date?"):
                start_date = get_date(click.prompt("Start Date(YYYY-MM-DD)"))
                end_date = get_date(click.prompt("End Date(YYYY-MM-DD)"))
                if use_user_list:
                    ulp.run_function_by_user_list(tweet_downloader.gen_user_tweets, user_or_user_list, twitter_getter,
                                                  user_tweets_setter, None, start_date, end_date)
                else:
                    tweet_downloader.gen_user_tweets(user_or_user_list, twitter_getter, user_tweets_setter, None,
                                                     start_date, end_date)
            else:
                if use_user_list:
                    ulp.run_function_by_user_list(tweet_downloader.gen_user_tweets, user_or_user_list, twitter_getter,
                                                  user_tweets_setter, None)
                else:
                    tweet_downloader.gen_user_tweets(user_or_user_list, twitter_getter, user_tweets_setter, None)
        elif tweet_type == 2:
            click.echo("Downloading Random Tweets")
            click.echo("Due to Tweepy constraints, if you want to download multiple tweets, you should launch a daemon")
            if click.confirm("Do you wish to launch a daemon to download random tweets?"):
                click.echo("Launching daemon")
                download_daemon.download_random_tweet()
            else:
                tweet_downloader.gen_random_tweet(twitter_getter, user_tweets_setter)
    elif download_type == 2:
        click.echo("Friend Download Types")
        click.echo("1. User Friends")
        click.echo("2. User Local Neighborhood")
        friend_type = click.prompt("Choose which to download", type=int)

        friends_downloader = BlueskyFriendsDownloader()
        if friend_type == 1:
            click.echo("Downloading user friends")
            use_user_list, user_or_user_list, ulp = get_user()
            # num_friends = click.prompt("Number of Friends(leave blank to get all)", type=int)
            if use_user_list:
                ulp.run_function_by_user_list(friends_downloader.gen_friends_ids_by_screen_name_or_id,
                                              user_or_user_list, twitter_getter, user_friends_setter, None)
            else:
                friends_downloader.gen_friends_ids_by_screen_name_or_id(user_or_user_list, twitter_getter,
                                                                        user_friends_setter, None)
        elif friend_type == 2:
            click.echo("Downloading user local neighborhood")
            use_user_list, user_or_user_list, ulp = get_user()
            if use_user_list:
                ulp.run_function_by_user_list(friends_downloader.gen_user_local_neighborhood, user_or_user_list,
                                              twitter_getter, user_friends_getter, user_friends_setter)
            else:
                friends_downloader.gen_user_local_neighborhood(user_or_user_list, twitter_getter, user_friends_getter,
                                                               user_friends_setter)
        else:
            raise Exception("Invalid input")
    elif download_type == 3:
        click.echo("Downloading followers")
        use_user_list, user_or_user_list, ulp = get_user()
        # num_followers = click.prompt("Number of Followers(leave blank to get all)", type=int)
        followers_downloader = BlueskyFollowersDownloader()
        if use_user_list:
            ulp.run_function_by_user_list(followers_downloader.gen_followers_by_screen_name_or_id, user_or_user_list,
                                          twitter_getter, user_followers_setter, None)
        else:
            followers_downloader.gen_followers_by_screen_name_or_id(user_or_user_list, twitter_getter,
                                                                    user_followers_setter, None)
    else:
        raise Exception("Invalid input")


def run_rt_processing():
    click.echo("Provide the full path the the raw tweet processing config(leave blank to set to default)")
    user_tweets_getter = dao_module.get_user_tweets_getter()
    user_processed_tweet_setter = dao_module.get_user_processed_tweets_setter()
    user_getter = dao_module.get_user_getter()
    tweet_processor = RawTweetProcessor()

    click.echo("Process Types")
    click.echo("1. Global(random) Tweets")
    click.echo("2. User Tweets")
    process_type = click.prompt("Choose what to process", type=int)

    if process_type == 1:
        click.echo("Processing global tweets")
        tweet_processor.gen_processed_tweets(user_tweets_getter, user_processed_tweet_setter)
    elif process_type == 2:
        click.echo("Processing user tweets")
        use_user_list, user_or_user_list, ulp = get_user()
        if use_user_list:
            ulp.run_function_by_user_list(tweet_processor.gen_processed_user_tweets, user_or_user_list,
                                          user_getter, user_tweets_getter, user_processed_tweet_setter)
        else:
            tweet_processor.gen_processed_user_tweets(user_or_user_list, user_getter, user_tweets_getter,
                                                      user_processed_tweet_setter)
    else:
        raise Exception("Invalid input")


def run_wf():
    user_processed_tweets_getter = dao_module.get_user_processed_tweets_getter()
    word_freq = WordFrequency()

    click.echo("Word Vector Types")
    click.echo("1. Global Word Count Vector")
    click.echo("2. Global Word Frequency Vector")
    click.echo("3. User Word Count Vector")
    click.echo("4. User Word Frequency Vector")
    click.echo("5. Relative User Word Frequency Vector")
    wf_type = click.prompt("Choose what to compute", type=int)

    if wf_type == 1:
        click.echo("Computing global word count vector")
        word_freq.gen_global_word_count_vector(user_processed_tweets_getter)
    elif wf_type == 2:
        click.echo("Computing global word frequency vector")
        wf_setter = dao_module.get_global_word_frequency_setter()
        word_freq.gen_global_word_frequency_vector(user_processed_tweets_getter, wf_setter)
    elif wf_type == 3:
        click.echo("Computing user word count vector")
        word_freq.gen_user_word_count_vector(user_processed_tweets_getter)
    elif wf_type == 4:
        click.echo("Computing user word frequency vector")
        wf_setter = dao_module.get_user_word_frequency_setter()
        word_freq.gen_user_word_frequency_vector(user_processed_tweets_getter, wf_setter)
    elif wf_type == 5:
        click.echo("Computing relative user word frequency vector")
        global_wf_getter = dao_module.get_global_word_frequency_getter()
        user_wf_getter = dao_module.get_user_word_frequency_getter()
        user_rwf_setter = dao_module.get_user_relative_word_frequency_setter()
        word_freq.gen_relative_user_word_frequency_vector(global_wf_getter, user_wf_getter, user_rwf_setter,
                                                          user_processed_tweets_getter)


def run_social_graph():
    user_getter = dao_module.get_user_getter()
    user_friends_getter = dao_module.get_user_friend_getter()
    social_graph_setter = dao_module.get_social_graph_setter()
    social_graph = SocialGraph()

    click.echo("Social Graph options")
    click.echo("1. User Friends Graph")
    social_graph_option = click.prompt("Choose what to compute", type=int)

    if social_graph_option == 1:
        click.echo("Computing user friends graph")
        click.echo("Reminder: make sure to have downloaded the local neighborhood for your user of interest")
        use_user_list, user_or_user_list, ulp = get_user()
        if use_user_list:
            ulp.run_function_by_user_list(social_graph.gen_user_friends_graph, user_or_user_list, user_friends_getter,
                                          social_graph_setter)
        else:
            social_graph.gen_user_friends_graph(user_or_user_list, user_getter, user_friends_getter,
                                                social_graph_setter)
    else:
        raise Exception("Invalid input")


def run_clustering():
    click.echo("Clustering Algorithms")
    click.echo("1. Affinity Propagation")
    click.echo("2. Label Propagation")
    click.echo("3. MUISI")
    clustering_type = click.prompt("Choose a clustering algorithm", type=int)

    if clustering_type == 1:
        click.echo("Computing Affinity Propagation cluster")
        ap = AffinityPropagation()
        default_path = get_project_root() / 'src' / 'process' / 'clustering' / 'affinity_propagation' / 'ap_config.yaml'
        ap_config_path = click.prompt("Path", default_path)
        ap_config_parser = AffinityPropagationConfigParser(ap_config_path)
        user_rwf_getter = dao_module.get_user_relative_word_frequency_getter()
        ap_setter = ap_config_parser.create_setter_DAOs()
        ap.gen_clusters(user_rwf_getter, ap_setter)
    elif clustering_type == 2:
        click.echo("Computing Label Propagation cluster")
        default_path = get_project_root() / 'src' / 'process' / 'clustering' / 'label_propagation' / 'lp_config.yaml'
        lp_config_path = click.prompt("Path", default_path)
        lp_config_parser = LabelPropagationConfigParser(lp_config_path)
        lp_cluster_setter = lp_config_parser.create_setter_DAOs()
        social_graph_getter = dao_module.get_social_graph_getter()

        user = click.prompt("User")
        lab_prop = LabelPropagation()
        user_id = dao_module.get_user_getter().get_user_by_screen_name(user).id
        lab_prop.gen_clusters(user_id, social_graph_getter, lp_cluster_setter)
    elif clustering_type == 3:
        click.echo("MUISI Variants")
        click.echo("1. Tweets")
        click.echo("2. Retweets")
        muisi_variant = click.prompt("Choose a variant", type=int)

        if muisi_variant == 1:
            click.echo("Computing MUISI cluster")
            default_path = get_project_root() / 'src' / 'process' / 'clustering' / 'muisi' / 'standard' / 'muisi_config.yaml'
            muisi_config_path = click.prompt("Path", default_path)
            muisi_config_parser = MUISIConfigParser(muisi_config_path, False)
            muisi_cluster_setter = muisi_config_parser.create_setter_DAOs()
            muisi = MUISI()

            # Get user args
            intersection_min = click.prompt("Intersection Min", type=float)
            popularity = click.prompt("Popularity", type=float)
            threshold = click.prompt("Threshold", type=float)
            user_count = click.prompt("User Count", type=int)
            item_count = click.prompt("Item Count", type=int)
            count = click.prompt("Count", type=int)
            is_only_popularity = click.confirm("Do you wish to only compute based on popularity?")
            muisi_config = MUISIConfig(intersection_min, popularity, threshold, user_count, item_count, count,
                                       is_only_popularity)

            user_wf_getter = dao_module.get_user_word_frequency_getter()
            user_rwf_getter = dao_module.get_user_relative_word_frequency_getter()
            muisi.gen_clusters(muisi_config, user_wf_getter, user_rwf_getter, muisi_cluster_setter)
        elif muisi_variant == 2:
            click.echo("Computing MUISI retweets cluster")
            default_path = get_project_root() / 'src' / 'process' / 'clustering' / 'muisi' / 'retweets' / 'muisi_retweets_config.yaml'
            muisi_config_path = click.prompt("Path", default_path)
            muisi_config_parser = MUISIConfigParser(muisi_config_path, True)
            tweet_getter = dao_module.get_user_tweets_getter()
            muisi_cluster_setter = muisi_config_parser.create_setter_DAOs()
            muisi = MUISIRetweet()

            # Get user args
            intersection_min = click.prompt("Intersection Min", type=float)
            popularity = click.prompt("Popularity", type=float)
            user_count = click.prompt("User Count", type=int)
            muisi_config = MUISIRetweetConfig(intersection_min, popularity, user_count)

            muisi.gen_clusters(muisi_config, tweet_getter, muisi_cluster_setter)
        else:
            raise Exception("Invalid input")
    else:
        raise Exception("Invalid input")


def run_community_expansion():
    click.echo("Community Expansion")
    click.echo("Assume initial users are CORE users. "
               "The cleaner initial users are, the better expansion result.")

    bluesky_getter = dao_module.get_bluesky_getter()
    user_tweets_getter = dao_module.get_user_tweets_getter()
    friends_getter = dao_module.get_user_friend_getter()
    user_getter = dao_module.get_user_getter()

    # TODO: test with different initial core users
    initial_user_list = ['irishrainforest.bsky.social', 'bethsawin.bsky.social', 'katharinehayhoe.com',
                         'easterncoyote.bsky.social', 'davidho.bsky.social', 'farhana.bsky.social',
                         'danielrembrandt.bsky.social', 'wyeates.bsky.social', 'climatenews.bsky.social',
                         'jksteinberger.bsky.social']

    # get user ids of the users in initial_user_list
    initial_user_list2 = []
    for initial_user in initial_user_list:
        initial_user_list2.append(bluesky_getter.get_user_by_screen_name(initial_user).id)
    initial_user_list = initial_user_list2

    file_path = str(get_project_root()) + "/data/community_expansion/"

    dataset_creator = DatasetCreator(
        file_path,
        user_getter,
        user_tweets_getter,
        friends_getter)

    core_refiner = CoreRefiner(user_getter,
                               user_tweets_getter,
                               friends_getter,
                               dataset_creator)

    initial_user_list = core_refiner.refine_core(
        top_size=5, core_size=20, potential_candidates_size=100, candidates_size_round1=50, candidates_size_round2=30,
        follower_threshold=0.4, large_account_threshold=1.5, low_account_threshold=0.05, friends_threshold=0.05,
        tweets_threshold=0.05, sosu_threshold=0.025, community=initial_user_list)

    algorithm = CommunityExpansionAlgorithm(
        user_getter,
        user_tweets_getter,
        friends_getter,
        dataset_creator)

    algorithm.expand_community(
        top_size=10, potential_candidates_size=1000, candidates_size_round1=500, candidates_size_round2=250,
        follower_threshold=0.2, large_account_threshold=2.0, low_account_threshold=0.025, friends_threshold=0.025,
        tweets_threshold=0.025, sosu_threshold=0.025, community=initial_user_list)


@click.command()
def main():
    click.echo("====================================================")
    click.echo("                       SNACES                       ")
    click.echo("Social Network Algorithm Contained Experiment System")
    click.echo("====================================================")
    click.echo("Processes:")
    click.echo("1. Download")
    click.echo("2. Raw Tweet Processing")
    click.echo("3. Word Frequency")
    click.echo("4. Social Graph")
    click.echo("5. Clustering")
    click.echo("6. Community Expansion")

    val = click.prompt("Choose a process")
    if int(val) == 1:
        run_download()
    elif int(val) == 2:
        run_rt_processing()
    elif int(val) == 3:
        run_wf()
    elif int(val) == 4:
        run_social_graph()
    elif int(val) == 5:
        run_clustering()
    elif int(val) == 6:
        run_community_expansion()
    else:
        raise Exception("Invalid input")


if __name__ == "__main__":
    main()
