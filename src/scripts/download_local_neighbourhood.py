import argparse
import time
from src.scripts.parser.parse_config import parse_from_file
from src.shared.utils import get_project_root
from src.dependencies.injector import Injector
from src.tools.user_list_processor import UserListProcessor

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
default_ul_path = get_project_root() / 'src' / 'tools' / 'user_list'

def download_local_neighbourhood(name: str, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    local_neighbourhood_downloader = process_module.get_local_neighbourhood_downloader("friends")
    local_neighbourhood_downloader.download_local_neighbourhood_by_screen_name(name)


if __name__ == "__main__":
    """
    Short script to download tweets
    """
    parser = argparse.ArgumentParser(description='Downloads the local neighbourhood of the given user')
    parser.add_argument('-n', '--name', dest='name', required=True,
        help='The name of the user to start on', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    download_local_neighbourhood(args.name, args.path)
