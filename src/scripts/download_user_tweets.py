import argparse
from src.shared.utils import get_project_root
from src.tools.user_list_processor import UserListProcessor
import src.dependencies.injector as sdi

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
default_ul_path = get_project_root() / 'src' / 'tools' / 'user_list'


def download_user_tweets(name: str, path=DEFAULT_PATH):
    injector = sdi.Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    bluesky_getter = dao_module.get_bluesky_getter()

    user_id = bluesky_getter.get_user_by_screen_name(name).id
    bluesky_getter.get_tweets_by_user_id(user_id, 1000)

    ulp = UserListProcessor()
    user_or_user_list = ulp.user_list_parser(default_ul_path)
    # for user_name in user_or_user_list:
    #     activity.download_user_tweets_by_screen_name(user_name)


if __name__ == "__main__":
    """
    Short script to download users
    """
    parser = argparse.ArgumentParser(description='Downloads the tweets for a given user')
    parser.add_argument('-n', '--screen_name', dest='name',
        help="The screen name of the user to download", required=True)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    download_user_tweets(args.name, args.path)
