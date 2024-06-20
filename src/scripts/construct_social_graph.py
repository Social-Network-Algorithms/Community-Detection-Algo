import argparse
from src.shared.utils import get_project_root
import src.dependencies.injector as sdi

DEFAULT_PATH = str(get_project_root()) + "/src/scripts/config/create_social_graph_and_cluster_config.yaml"


def construct_social_graph(seed_id: str, params=None, path=DEFAULT_PATH):
    injector = sdi.Injector.get_injector_from_file(path)
    process_module = injector.get_process_module()
    social_graph_constructor = process_module.get_social_graph_constructor("friends")
    social_graph_constructor.construct_social_graph(seed_id, params)


if __name__ == "__main__":
    """
    Short script to convert a local neighbourhood to a social graph
    """
    parser = argparse.ArgumentParser(description='Downloads the given number of tweets')
    parser.add_argument('-s', '--seed_id', dest='seed_id', required=True,
        help='The seed id of the local neighbourhood to convert into a social graph', type=str)
    parser.add_argument('-p', '--path', dest='path', required=False,
        default=DEFAULT_PATH, help='The path of the config file', type=str)

    args = parser.parse_args()

    construct_social_graph(args.seed_id, path=args.path)
