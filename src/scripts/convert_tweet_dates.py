import os
import sys

import argparse
import time

from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from src.model.local_neighbourhood import LocalNeighbourhood
import json
import logging
import random
import gc

log = LoggerFactory.logger(__name__, logging.ERROR)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

def process_dates(path=DEFAULT_PATH):

    injector = Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    user_tweet_getter: UserTweetsGetter = dao_module.get_user_tweets_getter()
    user_tweet_getter.convert_dates()

if __name__ == "__main__":
    """
    Short script to process tweets
    """
    parser = argparse.ArgumentParser(description='Processes the given tweet')

    parser.add_argument('-p', '--path', dest='path', required=False,
                        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    process_dates(args.path)
