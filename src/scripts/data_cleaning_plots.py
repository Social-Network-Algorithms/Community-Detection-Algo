import argparse
import matplotlib
import time
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
from src.process.data_cleaning.data_cleaning_distributions import DataCleaningDistributions

from src.model.local_neighbourhood import LocalNeighbourhood
import json

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/default_config.yaml"

def produce_plots(user_name: str, path=DEFAULT_PATH):

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    friends_getter = dao_module.get_user_friend_getter()
    user_getter = dao_module.get_user_getter()

    log.info("Getting seed user id")
    seed_id = str(user_getter.get_user_by_screen_name(user_name).get_id())

    plotter = DataCleaningDistributions(friends_getter, user_getter)

    log.info("Starting to plot")
    #plotter.tweet_plot(seed_id)
    #plotter.follower_plot(seed_id)
    #plotter.follower_ratio_plot(seed_id)
    plotter.local_friends_plot(seed_id)


if __name__ == "__main__":
    """
    Short script to produce scatter plots
    """
    parser = argparse.ArgumentParser(description='Short script to produce scatter plots of distributions')
    parser.add_argument('-n', '--screen_name', dest='name',
                        help="The screen name of the user to download", required=True)
    parser.add_argument('-p', '--path', dest='path', required=False,
                        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    produce_plots(args.name)
