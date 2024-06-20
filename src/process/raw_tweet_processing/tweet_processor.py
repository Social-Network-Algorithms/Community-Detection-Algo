from src.dao.user_processed_tweets.getter.user_processed_tweets_getter import UserProcessedTweetsGetter
from src.dao.user_processed_tweets.setter.user_processed_tweets_setter import UserProcessedTweetsSetter
from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.model.processed_tweet import ProcessedTweet
from src.model.local_neighbourhood import LocalNeighbourhood
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

class TweetProcessor():
    def __init__(self, user_tweets_getter: UserTweetsGetter, user_processed_tweet_getter: UserProcessedTweetsGetter,
                 user_processed_tweet_setter: UserProcessedTweetsSetter):
        self.user_tweets_getter = user_tweets_getter
        self.user_processed_tweet_getter = user_processed_tweet_getter
        self.user_processed_tweet_setter = user_processed_tweet_setter

    def process_tweet_by_id(self, id: str, user_id: str):
        all_user_tweets = self.user_tweets_getter.get_user_tweets(user_id)
        for tweet in all_user_tweets:
            if tweet.id == id:
                processed_tweet = ProcessedTweet.fromTweet(tweet)
                self.user_processed_tweet_setter.add_processed_tweets(user_id, [processed_tweet])
                return

    def process_tweets_by_user_id(self, user_id: str):
        tweets = self.user_tweets_getter.get_user_tweets(user_id)
        if tweets is not None:
            new_processed_tweets = []
            processed_tweets_ids = list(map(lambda x: x.id, self.user_processed_tweet_getter.get_user_processed_tweets(user_id)))
            for tweet in tweets:
                if tweet.id not in processed_tweets_ids:
                    processed_tweet = ProcessedTweet.fromTweet(tweet)
                    new_processed_tweets += processed_tweet
            self.user_processed_tweet_setter.add_processed_tweets(user_id, new_processed_tweets)
        log.info("Processed " + str(len(tweets)) + " Tweets for " + str(user_id))

    def process_tweets_by_user_list(self, user_ids):
        num_ids = len(user_ids)
        for i in range(num_ids):
            user_id = user_ids[i]
            self.process_tweets_by_user_id(user_id)
            log.log_progress(log, i, num_ids)

    def process_tweets_by_local_neighbourhood(self, local_neighbourhood: LocalNeighbourhood):
        user_ids = local_neighbourhood.get_user_id_list()
        self.process_tweets_by_user_list(user_ids)
