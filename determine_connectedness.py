from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def determine_connectedness():
    try:
        injector = Injector.get_injector_from_file(DEFAULT_PATH)
        process_module = injector.get_process_module()
        dao_module = process_module.dao_module
        user_getter = dao_module.get_user_getter()
        user_tweets_getter = dao_module.get_user_tweets_getter()
        user_friend_getter = dao_module.get_user_friend_getter()

        given_list =  ['jasondashbailey.bsky.social', 'aduralde.bsky.social', 'isaacbutler.bsky.social', 'jonathancohn.bsky.social', 'daveweigel.bsky.social', 'alishagrauso.bsky.social', 'helenkennedy.bsky.social', 'jamiroqueer.bsky.social', 'colson.bsky.social', 'schooley.bsky.social', 'mousterpiece.bsky.social']

        given_list_ids = []

        for u in given_list:
            given_list_ids.append(user_getter.get_user_by_screen_name(u).id)

        for i, name in enumerate(given_list):
            wanted_user_id = given_list_ids[i]
            all_tweets = user_tweets_getter.get_user_tweets(wanted_user_id)
            # the users in given_list who name has retweeted
            target_users = {}
            for tweet in all_tweets:
                original_user_id = tweet.retweet_user_id
                if original_user_id is not None:
                    if original_user_id in given_list_ids:
                        idx = given_list_ids.index(original_user_id)
                        if given_list[idx] not in target_users:
                            target_users[given_list[idx]] = 0
                        target_users[given_list[idx]] += 1

            target_users2 = []
            all_friends = user_friend_getter.get_user_friends_ids(wanted_user_id)
            for u in given_list_ids:
                if u in all_friends:
                    idx = given_list_ids.index(u)
                    target_users2.append(given_list[idx])

            print('the users who name: ' + name + ' has retweeted -> ', target_users)
            print('the users who are friends of name: ' + name + '-> ', target_users2)
            print('##############################################################################')


        # core_detector = process_module.get_jaccard_core_detector(activity)
        # core_detector.detect_core_by_screen_name(name, activity)
    except Exception as e:
        log.exception(e)
        exit()


if __name__ == "__main__":
    """
    Short script to determine the connectedness of the core users
    """
    determine_connectedness()
