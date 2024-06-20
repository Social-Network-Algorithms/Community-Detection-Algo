import argparse
import time
from src.scripts.parser.parse_config import parse_from_file
from src.shared.utils import get_project_root

from src.shared.logger_factory import LoggerFactory
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def download_tweets(user_name: str, path=DEFAULT_PATH):

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    user_friend_getter = dao_module.get_user_friend_getter()
    friends_cleaner = process_module.get_extended_friends_cleaner()
    user_getter = dao_module.get_user_getter()
    user_tweet_downloader = process_module.get_user_tweet_downloader()

    seed_id = user_getter.get_user_by_screen_name(user_name).id
    # Full user friend list
    # tweet_processor.process_tweets_by_user_list(init_user_friends)
    global_clean = friends_cleaner.clean_friends_global(seed_id, tweet_threshold=50,
                                                        follower_threshold=50, bot_threshold=0)
    clean_list10, removed_list10 = friends_cleaner.clean_friends_local(seed_id, global_clean, local_following=10)
    clean_list10.append(seed_id)

    user_tweet_downloader.download_user_tweets_by_user_list(clean_list10)


if __name__ == "__main__":
    """
    Short script to download tweets
    """
    parser = argparse.ArgumentParser(description='Downloads the tweets of all the users in a local neighbourhood of the given user')
    parser.add_argument('-n', '--name', dest='name', required=True,
                        help='The name of the user to start on', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
                        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    download_tweets(args.name, args.path)
