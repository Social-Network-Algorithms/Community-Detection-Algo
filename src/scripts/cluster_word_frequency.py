import argparse
from src.shared.utils import get_project_root
from src.dependencies.injector import Injector
from typing import List

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

def get_cluster_word_frequency(ids: List[str], path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()

    cluster_word_frequency_processor = process_module.get_cluster_word_frequency_processor()

    cluster_word_frequency_processor.process_cluster_word_frequency_vector(ids)
    cluster_word_frequency_processor.process_relative_cluster_word_frequency(ids)

if __name__ == "__main__":
    """
    Short script to download users
    """
    parser = argparse.ArgumentParser(description='Downloads the given user')
    parser.add_argument('-u', '--users', dest='users',
        help="The ids of the users to get cluster word frequency", required=True)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    users = args.users.split(",")

    get_cluster_word_frequency(users, args.path)