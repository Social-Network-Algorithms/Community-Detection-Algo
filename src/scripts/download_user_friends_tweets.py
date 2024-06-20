import argparse
import time
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
import logging

log = LoggerFactory.logger(__name__, logging.INFO)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/default_config.yaml"

def download_user_friends_tweets(id: str, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    process_module = injector.get_process_module()

    user_friend_getter = dao_module.get_user_friend_getter()
    user_tweet_downloader = process_module.get_user_tweet_downloader()

    log.info("Getting user friends for " + str(id))
    list = [id] + user_friend_getter.get_user_friends_ids(id)

    log.info("Beginning to download tweets for user " + str(id))
    user_tweet_downloader.download_user_tweets_by_user_list(list)


if __name__ == "__main__":
    """
    Short script to download tweets
    """
    parser = argparse.ArgumentParser(description='Downloads the tweets of all the users in a local neighbourhood of the given user')
    parser.add_argument('-i', '--id', dest='id', required=True,
        help='The name of the user to start on', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    download_user_friends_tweets(args.id, args.path)
