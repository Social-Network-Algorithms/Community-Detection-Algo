# import datetime
#
# from src.shared.utils import get_project_root
# from src.process.download.twitter_downloader import TwitterTweetDownloader, TwitterFriendsDownloader, TwitterFollowersDownloader
# from src.process.download.download_config_parser import DownloadConfigParser

# twitter_downloader = TwitterTweetDownloader()
# friends_downloader = TwitterFriendsDownloader()
# followers_downloader = TwitterFollowersDownloader()

# Init query variables
# id = "animesh_garg"
# start_date = datetime.datetime(2019, 6, 1, 0, 0, 0)
# end_date = datetime.datetime(2020, 7, 17, 0, 0, 0)

# Init input and output daos
# config_path = get_project_root() / 'src' / 'process' / 'download' / 'download_config.yaml'
# download_config_parser = DownloadConfigParser(config_path)
# tweepy_getter, user_friends_getter = download_config_parser.create_getter_DAOs()
# tweet_mongo_setter, user_friends_setter, user_followers_setter = download_config_parser.create_setter_DAOs()

# Test download
# twitter_downloader.gen_user_tweets(id, tweepy_getter, tweet_mongo_setter, 20)
# twitter_downloader.gen_user_tweets(id, tweepy_getter, tweet_mongo_setter, 20, start_date, end_date)
# twitter_downloader.gen_random_tweet(tweepy_getter, tweet_mongo_setter)
# friends_downloader.gen_friends_by_screen_name(id, tweepy_getter, user_friends_setter, 10)
# followers_downloader.gen_followers_by_screen_name(id, tweepy_getter, user_followers_setter, 10)

# Download local community for user; this should be done before running label propagation and user friend graph generation
# user = "hardmaru"
# friends_downloader.gen_user_local_neighborhood(user, tweepy_getter, user_friends_getter, user_friends_setter)

# Test user list processor on download
# from src.tools.user_list_processor import UserListProcessor
# ulp = UserListProcessor()
# user_list_file_path = get_project_root() / 'src' / 'tools' / 'user_list'
# user_list = ulp.user_list_parser(user_list_file_path)
# ulp.run_function_by_user_list(twitter_downloader.gen_user_tweets, user_list, tweepy_getter, tweet_mongo_setter, 5)
