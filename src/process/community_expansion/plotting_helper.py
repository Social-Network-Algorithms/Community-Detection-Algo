from matplotlib import pyplot as plt

from src.shared.utils import get_project_root


def graph_plots(initial_seed, track_users_list, community_social_support_ranker):
    """graph social support ranker score vs the adding order for the expanded community"""
    scores = community_social_support_ranker.score_users(track_users_list, track_users_list)
    path = str(get_project_root()) + "/data/expansion/" + initial_seed + "/final expansion (social support (retweets))"
    plt.figure("final expansion (social support (retweets))")
    plt.bar(list(range(0, len(track_users_list))), list(scores.values()))
    plt.ylabel('Final social support score')
    plt.xlabel('Adding order of users')
    plt.title('Final score of users in the final community')
    plt.savefig(path)
