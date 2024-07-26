from src.shared.logger_factory import LoggerFactory
import src.dependencies.injector as sdi
from src.shared.utils import get_project_root

path = str(get_project_root()) + \
       "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
log = LoggerFactory.logger(__name__)
injector = sdi.Injector.get_injector_from_file(path)
process_module = injector.get_process_module()
dao_module = injector.get_dao_module()
user_getter = dao_module.get_user_getter()
friends_getter = dao_module.get_user_friend_getter()
user_tweets_getter = dao_module.get_user_tweets_getter()
user_downloader = process_module.get_user_downloader()
user_tweet_downloader = process_module.get_user_tweet_downloader()
friend_downloader = process_module.get_friend_downloader()


def download_friends(curr_candidates):
    for curr_candidate in curr_candidates:
        friend_list = friends_getter.get_user_friends_ids(curr_candidate)
        if friend_list is None:
            log.info("Download friends of " + str(curr_candidate))
            friend_downloader.download_friends_ids_by_id(curr_candidate)


def download_user_info_and_tweets(curr_candidates):
    user_ids = []
    for curr_candidate in curr_candidates:
        user_info = user_getter.get_user_by_id(curr_candidate)
        user_id = None
        if user_info is None:
            try:
                log.info("Download user " + str(curr_candidate))
                user_downloader.download_user_by_id(curr_candidate)
                user_info = user_getter.get_user_by_id(curr_candidate)
                user_id = user_info.id
            except Exception:
                log.info("[Download Error] Cannot download user " + str(curr_candidate))
        else:
            user_id = user_info.id

        if user_id is not None:
            tweets_list = user_tweets_getter.get_user_tweets(user_id)
            if tweets_list is None:
                log.info("Download tweets of " + str(user_id))
                user_tweet_downloader.download_user_tweets_by_user_id(user_id)

            user_ids.append(user_id)

    return user_ids
