import src.dependencies.injector as sdi
from src.shared.utils import get_project_root

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def rank_users(cluster, path=DEFAULT_PATH):
    """Returns the top 10 ranked users from the given cluster with the seed id as user's id."""
    injector = sdi.Injector.get_injector_from_file(path)
    dao_module = injector.get_dao_module()
    process_module = injector.get_process_module()
    sosu_ranker = process_module.get_ranker("SocialSupport")
    scores = sosu_ranker.score_users(cluster.users)
    user_getter = dao_module.get_user_getter()
    top_n_users = [user_getter.get_user_by_id(u).screen_name for u in scores]
    return top_n_users
