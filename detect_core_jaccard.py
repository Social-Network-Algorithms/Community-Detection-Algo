import argparse
import time
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def detect_core(name: int, activity: str, path=DEFAULT_PATH):
    try:
        injector = Injector.get_injector_from_file(path)
        process_module = injector.get_process_module()

        core_detector = process_module.get_jaccard_core_detector(activity)
        core_detector.detect_core_by_screen_name(name, activity)
    except Exception as e:
        log.exception(e)
        exit()


if __name__ == "__main__":
    """
    Short script to download tweets
    """
    # act: friends, user retweets, user retweets ids
    parser = argparse.ArgumentParser(description='Downloads the given number of tweets')
    parser.add_argument('-n', '--name', dest='name', required=True,
        help='The name of the user to start on', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)
    parser.add_argument('-act', '--activity', dest='activity', required=True,
        help='The user activity', type=str)

    args = parser.parse_args()

    detect_core(args.name, args.activity, args.path)
