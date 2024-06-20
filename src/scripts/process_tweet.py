import argparse
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/process_tweet_config.yaml"


def process_tweet(id: str, user: str, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    process_module = injector.get_process_module()
    user_getter = dao_module.get_user_getter()

    user_id = user_getter.get_user_by_screen_name(user).id
    tweet_processor = process_module.get_tweet_processor()
    tweet_processor.process_tweet_by_id(id, user_id)


if __name__ == "__main__":
    """
    Short script to process tweets
    """
    parser = argparse.ArgumentParser(description='Processes the given tweet for the given user')
    parser.add_argument('-i', '--id', dest='id',
        help="The id of the tweet to process", required=True, type=str)
    parser.add_argument('-user', '--user', dest='user',
                        help="The user name of the associated user", required=True, type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    process_tweet(args.id, args.user, args.path)
