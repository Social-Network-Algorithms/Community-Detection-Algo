import schedule
import daemon
import time

from src.shared.utils import get_project_root
import src.dependencies.injector as sdi

DEFAULT_PATH = str(get_project_root()) + \
                   "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

def download_random_tweet():
    def main():
        injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
        process_module = injector.get_process_module()
        tweet_downloader = process_module.get_tweet_downloader()
        tweet_downloader.get_random_tweet()

    with daemon.DaemonContext(chroot_directory=None, working_directory='./'):
        # schedule every second, rather than every day
        schedule.every().second.do(main)

        while True:
            schedule.run_pending()
            time.sleep(1)