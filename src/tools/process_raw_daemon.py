import schedule
import daemon
import time

from src.shared.utils import get_project_root
from src.process.raw_tweet_processing.raw_tweet_processor import RawTweetProcessor
import src.dependencies.injector as sdi

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

def process_raw_tweet():
    def main():
        raw_processor = RawTweetProcessor()
        injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
        dao_module = injector.get_dao_module()
        tweet_getter = dao_module.get_user_tweets_getter()
        user_processed_tweet_setter = dao_module.get_user_processed_tweets_getter()
        raw_processor.gen_processed_tweets(tweet_getter, user_processed_tweet_setter)

    with daemon.DaemonContext(chroot_directory=None, working_directory='./'):
        # schedule every second, rather than every day
        schedule.every().day.do(main)

        while True:
            schedule.run_pending()
            time.sleep(1)
