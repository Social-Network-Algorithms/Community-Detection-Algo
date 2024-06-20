import argparse
import time
from src.dependencies.injector import Injector
from src.shared.utils import get_project_root
from src.shared.logger_factory import LoggerFactory
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from src.model.local_neighbourhood import LocalNeighbourhood
import json

log = LoggerFactory.logger(__name__)

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/default_config.yaml"

def produce_plots(seed_id: str, user_name: str, path=DEFAULT_PATH):
    threshold = 60

    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    user_friend_getter = dao_module.get_user_friend_getter()
    friends_cleaner = process_module.get_friends_cleaner()
    social_graph_constructor = process_module.get_social_graph_constructor()
    clusterer = process_module.get_clusterer()
    cluster_word_frequency_processor = process_module.get_cluster_word_frequency_processor()

    tweet_processor = process_module.get_tweet_processor()

    production_ranker = process_module.get_ranker()
    consumption_ranker = process_module.get_ranker(type="Consumption")
    follower_ranker = process_module.get_ranker(type="Follower")

    # Full user friend list
    init_user_friends = user_friend_getter.get_user_friends_ids(seed_id)
    # tweet_processor.process_tweets_by_user_list(init_user_friends)
    clean_list = friends_cleaner.clean_friends_from_list(seed_id, init_user_friends, percent_threshold=threshold)
    clean_list = [str(id) for id in clean_list]
    init_user_dict = get_local_neighbourhood_user_dict(seed_id, clean_list, user_friend_getter)
    local_neighbourhood = LocalNeighbourhood(seed_id=seed_id, params=None, users=init_user_dict)
    social_graph = social_graph_constructor.construct_social_graph_from_local_neighbourhood(seed_id, local_neighbourhood)
    clusters = clusterer.cluster_by_social_graph(seed_id, social_graph, {})

    count = 1
    for cluster in clusters:
        if len(cluster.users) < 5:
            continue

        prod_ranking, prod_scores = production_ranker.rank(seed_id, cluster)
        cons_ranking, cons_scores = consumption_ranker.rank(seed_id, cluster)
        foll_ranking, foll_scores = follower_ranker.rank(seed_id, cluster)

        cluster_wf_vector = cluster_word_frequency_processor.process_cluster_word_frequency_vector(cluster.users)

        wf_dict = cluster_wf_vector.get_words_dict()
        sorted_words = list(sorted(wf_dict, key=wf_dict.get, reverse=True))
        sorted_words.remove("rt")
        sorted_words.remove("like")
        top_words = sorted_words[0:min(len(sorted_words), 10)]

        file_prefix = user_name + '_' + str(count)

        scatter_plot_from_scores(user_name, prod_scores, cons_scores, count, top_words, file_prefix + "prod_cons")
        scatter_plot_from_scores(user_name, prod_scores, cons_scores, count, top_words, file_prefix + "prod_cons", use_log_log_scale=True)

        scatter_plot_from_scores(user_name, prod_scores, foll_scores, count, top_words, file_prefix + "prod_foll", type1='Production Utility', type2='Follower Utility')
        scatter_plot_from_scores(user_name, prod_scores, foll_scores, count, top_words, file_prefix + "prod_foll", use_log_log_scale=True, type1='Production Utility', type2='Follower Utility')

        scatter_plot_from_scores(user_name, cons_scores, foll_scores, count, top_words, file_prefix + "cons_foll", type1='Consumption Utility', type2='Follower Utility')
        scatter_plot_from_scores(user_name, cons_scores, foll_scores, count, top_words, file_prefix + "cons_foll", use_log_log_scale=True, type1='Consumption Utility', type2='Follower Utility')

        write_scores_to_file({"production": prod_scores, "consumption": cons_scores, "follower": foll_scores}, user_name, count)
        count += 1

def write_scores_to_file(scores, user_name, number):
    filename = (user_name + '_' + str(number) + '_scores.json')
    with open(filename, 'w') as file:
        json.dump(scores, file)

def get_local_neighbourhood_user_dict(seed_id, init_user_friends, user_friend_getter):
    user_dict = {}

    user_dict[str(seed_id)] = init_user_friends

    for curr_id in init_user_friends:
        curr_user_friends = user_friend_getter.get_user_friends_ids(curr_id)
        curr_user_friends = [str(id) for id in curr_user_friends if (str(id) in init_user_friends)]
        user_dict[str(curr_id)] = curr_user_friends

    return user_dict

def scatter_plot_from_scores(user_name, scores1, scores2, number, top_words, prefix, type1='Production Utility', type2='Consumption Utility', use_log_log_scale=False):
    keys = scores1.keys()
    x = []
    y = []
    for key in keys:
        x.append(scores1[str(key)])
        y.append(scores2[str(key)])

    top_words_str = str(top_words)[1:-1]

    suffix = '' if not use_log_log_scale else ' (Log-Log scale)'

    plt.suptitle(type1 +  ' vs ' + type2 + suffix)
    plt.title("Cluster " + str(number) + ", Top " + str(len(top_words)) + " Words: " + top_words_str, fontsize='small')
    plt.grid(axis='x', alpha=0.75)
    plt.grid(axis='y', alpha=0.75)

    if use_log_log_scale:
        plt.xscale('log')
        plt.yscale('log')

    plt.xlabel(type1)
    plt.ylabel(type2)
    plt.plot(x, y, '.', color='blue')
    # plt.show()
    filename = prefix + '.png' if not use_log_log_scale \
        else prefix + '_logscale.png'

    plt.savefig(filename, dpi=300)
    plt.clf()


if __name__ == "__main__":
    """
    Short script to produce scatter plots
    """
    parser = argparse.ArgumentParser(description='Short script to produce scatter plots of utility')
    parser.add_argument('-i', '--seed_id', dest='id',
        help="The id of the user to download", required=True)
    parser.add_argument('-n', '--screen_name', dest='name',
        help="The screen name of the user to download", required=True)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    produce_plots(args.id, args.name)
