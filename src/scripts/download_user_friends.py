import argparse
import time
from src.shared.utils import get_project_root
from src.dependencies.injector import Injector
from src.tools.user_list_processor import UserListProcessor

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
default_ul_path = get_project_root() / 'src' / 'tools' / 'user_list'

def download_user_friends(name: str, saturated=False, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()

    user_friend_downloader = process_module.get_friend_downloader()
    # if saturated:
    #     user_friend_downloader.download_friends_users_by_screen_name(name)
    # else:
    #     user_friend_downloader.download_friends_ids_by_screen_name(name)

    ulp = UserListProcessor()
    user_or_user_list = ulp.user_list_parser(default_ul_path)
    for user_name in user_or_user_list:
        if saturated:
            user_friend_downloader.download_friends_users_by_screen_name(user_name)
        else:
            user_friend_downloader.download_friends_ids_by_screen_name(user_name)

if __name__ == "__main__":
    """
    Short script to download users
    """
    parser = argparse.ArgumentParser(description='Downloads the given user')
    parser.add_argument('-n', '--screen_name', dest='name',
        help="The screen name of the user to download", required=True)
    parser.add_argument('-s', '--saturated', dest='saturated', required=False,
        action='store_true',
        help='If true, downloads full user objects, otherwise just downloads ids')
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    download_user_friends(args.name, saturated=args.saturated, path=args.path)
