from src.shared.utils import get_project_root
from src.process.clustering.label_propagation.label_propagation import LabelPropagation
from src.process.clustering.label_propagation.lp_config_parser import LabelPropagationConfigParser

# Init input and output daos
# config_path = get_project_root() / 'src' / 'process' / 'clustering' / 'label_propagation' / 'lp_config.yaml'
# lp_config_parser = LabelPropagationConfigParser(config_path)
# social_graph_getter = lp_config_parser.create_getter_DAOs()
# lp_cluster_setter = lp_config_parser.create_setter_DAOs()

# Run tests
# user = "hardmaru"
# Download local community for user(this is done in the download sanity test)
# Generate User Friends Graph(this is done in the social graph sanity test)

# Run label propagation to get clusters
# lab_prop = LabelPropagation()
# lab_prop.gen_clusters(user, social_graph_getter, lp_cluster_setter)
