import argparse
from src.shared.utils import get_project_root
from src.dependencies.injector import Injector

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def process_user_tweets(id: str, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()

    tweet_processor = process_module.get_tweet_processor()

    tweet_processor.process_tweets_by_user_id(id)


if __name__ == "__main__":
    """
    Short script to process the tweets of a Local Neighbourhood
    """
    parser = argparse.ArgumentParser(description='Processes the tweets of the given user')
    parser.add_argument('-i', '--id', dest='id', required=True,
        help='The id of the user', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    process_user_tweets(args.id, args.path)
