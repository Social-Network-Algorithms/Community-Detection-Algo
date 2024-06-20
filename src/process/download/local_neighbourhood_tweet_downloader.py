from src.process.download.user_tweet_downloader import UserTweetDownloader
from src.dao.local_neighbourhood.getter.local_neighbourhood_getter import LocalNeighbourhoodGetter
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)


class LocalNeighbourhoodTweetDownloader():
    """
    Download tweets for a local neighbourhood
    """

    def __init__(self, user_tweet_downloader: UserTweetDownloader, local_neighbourhood_getter: LocalNeighbourhoodGetter):
        self.user_tweet_downloader = user_tweet_downloader
        self.local_neighbourhood_getter = local_neighbourhood_getter

    def download_user_tweets_by_local_neighbourhood(self, seed_id: str, params=None):
        log.info("Starting Tweet Download for local neighbourhood of " + str(seed_id))

        local_neighbourhood = self.local_neighbourhood_getter.get_local_neighbourhood(seed_id, params)
        user_ids = local_neighbourhood.get_user_id_list()

        self.user_tweet_downloader.download_user_tweets_by_user_list(user_ids)
