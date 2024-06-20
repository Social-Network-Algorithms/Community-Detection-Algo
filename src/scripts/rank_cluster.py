import argparse
from src.shared.utils import get_project_root
from src.scripts.parser.parse_config import parse_from_file
from src.dependencies.injector import Injector

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config//src/scripts/config/create_social_graph_and_cluster_config.yaml"

def rank_cluster(seed_id: str, params=None, path=DEFAULT_PATH):
    injector = Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    dao_module = injector.get_dao_module()

    cluster_getter = dao_module.get_cluster_getter()
    ranker = process_module.get_ranker('Consumption')

    clusters, _ = cluster_getter.get_clusters(seed_id)

    for cluster in clusters:
        ranker.rank(seed_id, cluster)

if __name__ == "__main__":
    """
    Short script to perform clustering on a social graph
    """
    parser = argparse.ArgumentParser(description='Downloads the given number of tweets')
    parser.add_argument('-s', '--seed_id', dest='seed_id', required=True,
        help='The seed id of the local neighbourhood to convert into a social graph', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    rank_cluster(args.seed_id, path=args.path)
