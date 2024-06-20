# from src.shared.utils import get_project_root
# from src.process.clustering.MUISI.standard.muisi import MUISI, MUISIConfig
# from src.process.clustering.MUISI.muisi_config_parser import MUISIConfigParser

# Init input and output daos
# config_path = get_project_root() / 'src' / 'process' / 'clustering' / 'muisi' / 'standard' / 'muisi_config.yaml'
# muisi_config_parser = MUISIConfigParser(config_path, False)
# wf_getter = muisi_config_parser.create_getter_DAOs()
# muisi_cluster_setter = muisi_config_parser.create_setter_DAOs()

# Run tests
# intersection_min = 2
# popularity = 0.3
# threshold = 0.5
# user_count = 5
# item_count = 5
# count = 5
# is_only_popularity = True
# muisi_config = MUISIConfig(intersection_min, popularity, threshold, user_count,
#                  item_count, count, is_only_popularity)
#
# muisi = MUISI()
# muisi.gen_clusters(muisi_config, wf_getter, muisi_cluster_setter)
