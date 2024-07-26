import src.dependencies.injector as sdi
from matplotlib import pyplot as plt

from src.process.community_ranking.community_consumption_utility_ranker import CommunityConsumptionUtilityRanker
from src.process.community_ranking.community_influence_one_ranker import CommunityInfluenceOneRanker
from src.process.community_ranking.community_influence_two_ranker import CommunityInfluenceTwoRanker
from src.process.community_ranking.community_production_utility_ranker import CommunityProductionUtilityRanker
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker
from src.shared.utils import get_project_root

path = str(get_project_root()) + \
       "/src/scripts/config/create_social_graph_and_cluster_config.yaml"
injector = sdi.Injector.get_injector_from_file(path)
process_module = injector.get_process_module()
dao_module = injector.get_dao_module()
friends_getter = dao_module.get_user_friend_getter()
user_tweets_getter = dao_module.get_user_tweets_getter()


def graph_progress(x_vals, y_vals, fig_name):
    """Graphs the plot of ranking score vs the add order for the final expanded community"""
    path = str(get_project_root()) + "/data/community_expansion/" + fig_name
    plt.figure(fig_name)
    plt.bar(x_vals, y_vals)
    plt.ylabel('Final Rank')
    plt.xlabel('Adding order')
    plt.title('Final rank vs adding order in the ' + fig_name)
    plt.savefig(path)


def graph_plots(track_users_list):

    # graph each ranker score vs the adding order for the expanded community
    # community_influence1_ranker = CommunityInfluenceOneRanker(user_tweets_getter, friends_getter, None)
    # community_influence2_ranker = CommunityInfluenceTwoRanker(user_tweets_getter, friends_getter, None)
    # community_production_ranker = CommunityProductionUtilityRanker(user_tweets_getter, friends_getter, None)
    # community_consumption_ranker = CommunityConsumptionUtilityRanker(user_tweets_getter, friends_getter, None)
    # ranker_list = [community_influence1_ranker, community_influence2_ranker, community_production_ranker,
    #                community_consumption_ranker]
    # for ranker in ranker_list:
    #     scores = ranker.score_users(track_users_list, track_users_list)
    #     graph_progress(list(range(0, len(track_users_list))), list(scores.values()),
    #                    "final expansion (" + str(ranker.ranking_function_name) + ")")

    # graph social support ranker score vs the adding order for the expanded community
    community_social_support_ranker = CommunitySocialSupportRanker(user_tweets_getter, friends_getter, None)
    scores = community_social_support_ranker.score_users(track_users_list, track_users_list)
    graph_progress(list(range(0, len(track_users_list))), list(scores.values()),
                   "final expansion (social support (retweets))")
