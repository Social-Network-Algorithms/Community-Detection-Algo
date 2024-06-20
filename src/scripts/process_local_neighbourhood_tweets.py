import argparse
import time
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def process_local_neighbourhood_tweets(id: str, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    process_module = injector.get_process_module()

    local_neighbourhood_getter = dao_module.get_local_neighbourhood_getter()
    tweet_processor = process_module.get_tweet_processor()

    local_neighbourhood = local_neighbourhood_getter.get_local_neighbourhood(id)
    tweet_processor.process_tweets_by_local_neighbourhood(local_neighbourhood)

if __name__ == "__main__":
    """
    Short script to process the tweets of a Local Neighbourhood
    """
    parser = argparse.ArgumentParser(description='Processes the tweets of all the users in a local neighbourhood of the given user')
    parser.add_argument('-i', '--id', dest='id', required=True,
        help='The seed id of the local neighbourhood', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    process_local_neighbourhood_tweets(args.id, args.path)
