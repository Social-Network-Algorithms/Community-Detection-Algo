# from src.shared.utils import get_project_root
# from src.process.word_frequency.word_frequency import WordFrequency
# from src.process.word_frequency.wf_config_parser import WordFrequencyConfigParser

# word_freq = WordFrequency()

# Init input and output daos
# config_path = get_project_root() / 'src' / 'process' / 'word_frequency' / 'wf_config.yaml'
# wf_config_parser = WordFrequencyConfigParser(config_path)
# processed_tweet_getter, wf_getter = wf_config_parser.create_getter_DAOs()
# processed_tweet_setter, wf_setter = wf_config_parser.create_setter_DAOs()

# Run tests
# word_freq.gen_global_word_count_vector(processed_tweet_getter, processed_tweet_setter, wf_setter)
# word_freq.gen_global_word_frequency_vector(wf_getter, wf_setter)

# word_freq.gen_user_word_count_vector(processed_tweet_getter, processed_tweet_setter, wf_setter)
# word_freq.gen_user_word_frequency_vector(wf_getter, wf_setter)

# word_freq.gen_relative_user_word_frequency_vector(wf_getter, wf_setter)
