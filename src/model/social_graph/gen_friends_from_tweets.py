import src.dependencies.injector as sdi
from src.shared.logger_factory import LoggerFactory
from src.shared.utils import get_project_root, jaccard_similarity
from src.model.local_neighbourhood import LocalNeighbourhood
# Just for type signatures
from typing import List
from src.model.user import User
from src.model.social_graph.social_graph import SocialGraph
from src.model.cluster import Cluster
import argparse

log = LoggerFactory.logger(__name__)
DEFAULT_PATH = str(get_project_root()) + \
    "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def generate_friend_graph_from_tweets(tweet_thresh=1, path=DEFAULT_PATH):

    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    def generate_user_friends_from_tweets(user_id: int, tweet_thresh: int, path=DEFAULT_PATH):
        try:
            # log.info(f"Creating friend graph of {screen_name} from tweets")

            tweet_getter = dao_module.get_user_tweets_getter()
            friend_setter = dao_module.get_retweeted_users_setter()

            retweets = tweet_getter.get_user_retweets(user_id)
            dic = {}
            # If number of retweets of tweets from retweet user is greater than threshold, add to friend set
            for retweet in retweets:
                if retweet.retweet_user_id in dic:
                    dic[retweet.retweet_user_id] += 1
                else:
                    dic[retweet.retweet_user_id] = 1

            friends = [k for k, v in dic.items() if v >= tweet_thresh]
            # evaluate_friends_list(dao_module.get_user_friend_getter(), user.id, friends)
            friend_setter.store_friends(user_id, friends)
        except Exception as e:
            log.exception(e)
            log.exception(f'{user_id} {type(user_id)}')
            return

    user_getter = dao_module.get_user_getter()
    users = user_getter.get_all_users()

    for user_id in users:
        generate_user_friends_from_tweets(user_id, tweet_thresh, path)


def evaluate_friends_list(friend_getter, user_id, friends: List[int]):
    original_friends = friend_getter.get_user_friends_ids(user_id)
    # Compare the two lists

    # Lengths
    log.info(f'Original friends: {len(original_friends)}')
    log.info(f'New friends: {len(friends)}')

    # Number in common
    log.info(
        f'Number in common: {len(set(original_friends).intersection(set(friends)))}')

    # Jaccard similarity
    log.info(
        f'Jaccard similarity: {jaccard_similarity(original_friends, friends)}')


if __name__ == "__main__":
    generate_friend_graph_from_tweets(1)
