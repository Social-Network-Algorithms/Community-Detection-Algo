from src.dependencies.injector import Injector

import argparse
import time
from src.scripts.parser.parse_config import parse_from_file
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
from datetime import datetime
import logging
log = LoggerFactory.logger(__name__, logging.ERROR)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def get_tweets(name: str, path=DEFAULT_PATH):

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    user_getter = dao_module.get_user_getter()
    user_id = user_getter.get_user_by_screen_name(name).id
    twitter_getter = dao_module.get_twitter_getter()
    # tweets = twitter_getter.get_tweets_by_user_id(user_id)
    user_tweet_getter = dao_module.get_user_tweet_getter()
    tweets = sorted(user_tweet_getter.get_tweets_by_user_id_time_restricted(str(user_id)),
                    key=lambda x: x.created_at)
    log.info(len(tweets))
    log.info(tweets[0].text)
    tweet = tweets[0]
    date = tweet.created_at
    log.info(date)

    if type(date) != datetime:
        proper_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        tweet.created_at = proper_date
    log.info(tweet.__dict__)


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

    get_tweets(args.name, args.path)
