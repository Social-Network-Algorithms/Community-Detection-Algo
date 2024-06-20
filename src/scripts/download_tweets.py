import argparse
import time
from src.shared.utils import get_project_root
import src.dependencies.injector as sdi

DEFAULT_PATH = str(get_project_root()) + \
                   "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def download_tweets(num: int, path=DEFAULT_PATH):
    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    tweet_downloader = process_module.get_tweet_downloader()
    for _ in range(num):
        tweet_downloader.get_random_tweet()

if __name__ == "__main__":
    """
    Short script to download tweets
    """
    parser = argparse.ArgumentParser(description='Downloads the given number of tweets')
    parser.add_argument('-n', '--num', dest='num', required=True,
        help='The number of tweets to download', type=int)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    download_tweets(args.num, args.path)
