# from src.shared.utils import get_project_root
# from src.process.raw_tweet_processing.raw_tweet_processor import RawTweetProcessor
# from src.process.raw_tweet_processing.rt_processing_config_parser import RawTweetProcessingConfigParser

# tweet_processor = RawTweetProcessor()

# Init input and output daos
# config_path = get_project_root() / 'src' / 'process' / 'raw_tweet_processing' / 'rt_processing_config.yaml'
# rt_processing_config_parser = RawTweetProcessingConfigParser(config_path)
# tweet_getter = rt_processing_config_parser.create_getter_DAOs()
# tweet_setter, processed_tweet_setter = rt_processing_config_parser.create_setter_DAOs()

# Run tests
# tweet_processor.gen_processed_global_tweets(tweet_getter, tweet_setter, processed_tweet_setter)
# tweet_processor.gen_processed_user_tweets(tweet_getter, tweet_setter, processed_tweet_setter)
