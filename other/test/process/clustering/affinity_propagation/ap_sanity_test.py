from src.shared.utils import get_project_root
from src.process.clustering.affinity_propagation.affinity_propagation import AffinityPropagation
from src.process.clustering.affinity_propagation.ap_config_parser import AffinityPropagationConfigParser

# aff_prop = AffinityPropagation()

# Init input and output daos
# config_path = get_project_root() / 'src' / 'process' / 'clustering' / 'affinity_propagation' / 'ap_config.yaml'
# ap_config_parser = AffinityPropagationConfigParser(config_path)
# wf_getter = ap_config_parser.create_getter_DAOs()
# aff_prop_setter = ap_config_parser.create_setter_DAOs()

# Run tests
# clusters = aff_prop.gen_clusters(wf_getter, aff_prop_setter)
