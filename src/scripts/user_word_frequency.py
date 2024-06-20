import argparse
from src.shared.utils import get_project_root
from src.dependencies.injector import Injector

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def get_user_word_frequency(id, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()

    user_word_frequency_processor = process_module.get_user_word_frequency_processor()

    user_word_frequency_processor.process_user_word_frequency_vector(id)
    user_word_frequency_processor.process_relative_user_word_frequency(id)

if __name__ == "__main__":
    """
    Short script to download users
    """
    parser = argparse.ArgumentParser(description='Downloads the given user')
    parser.add_argument('-u', '--name', dest='name',
        help="The id of the user to get word frequency", required=True)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()
    users = args.name.split(",")
    for user in users:
        get_user_word_frequency(user, args.path)


    # if isinstance(args.name, list):
    #     for user_ids in args.name:
    #         get_user_word_frequency(args.name, args.path)
    # else:
    #     get_user_word_frequency(args.name, args.path)