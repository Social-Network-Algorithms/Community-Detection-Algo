import src.dependencies.injector as sdi
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
from src.model.local_neighbourhood import LocalNeighbourhood
from typing import List
from src.model.user import User
import argparse

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + \
"/src/scripts/config/create_social_graph_and_cluster_config.yaml"
def main(screen_name, user_activity: str):

    path = DEFAULT_PATH
    log.info(f"Downloading local neighbourhood with activity={user_activity} for user={screen_name}")

    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()
    local_neighbourhood_getter = dao_module.get_local_neighbourhood_getter(user_activity)
    user = get_user_by_screen_name(screen_name, path)

    local_neighbourhood_downloader = process_module.get_local_neighbourhood_downloader(user_activity)
    local_neighbourhood_downloader.download_local_neighbourhood_by_id(
        user.id)
    local_neighbourhood = local_neighbourhood_getter.get_local_neighbourhood(
        user.id)
    log.info(local_neighbourhood.__dict__)
    
def get_user_by_screen_name(screen_name: str, path=DEFAULT_PATH) -> User:
    """Returns a user object from their bluesky screen name."""
    injector = sdi.Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    user_getter = dao_module.get_user_getter()
    user = user_getter.get_user_by_screen_name(screen_name)
    return user

if __name__ == "__main__":
    """
    Short script to download local nbhds
    """
    # act: friends, user retweets, user retweets ids
    parser = argparse.ArgumentParser(description='Parses')
    parser.add_argument('-act', '--activity', dest='activity', required=True,
        help='The user activity', type=str)
    parser.add_argument('-n', '--name', dest='name', required=True,
        help='The name of the user to start on', type=str)

    args = parser.parse_args()

    main(args.name, args.activity)