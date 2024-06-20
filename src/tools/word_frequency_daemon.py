import schedule
import daemon
import time

from src.shared.utils import get_project_root
from src.process.word_frequency.word_frequency import WordFrequency
import src.dependencies.injector as sdi

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"

def make_word_frequency():
    def global_word_count():
        word_frequency = WordFrequency()
        injector = sdi.Injector.get_injector_from_file(DEFAULT_PATH)
        dao_module = injector.get_dao_module()
        user_processed_tweets_getter = dao_module.get_user_processed_tweets_getter()
        word_frequency.gen_global_word_count_vector(user_processed_tweets_getter)

    with daemon.DaemonContext(chroot_directory=None, working_directory='./'):
        # schedule every second, rather than every day
        schedule.every().day.at("0:00").do(global_word_count)

        while True:
            schedule.run_pending()
            time.sleep(1)
