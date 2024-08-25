import nltk
import re
import datetime

from src.dao.user.getter.user_getter import UserGetter
from src.dao.user_processed_tweets.setter.user_processed_tweets_setter import UserProcessedTweetsSetter
from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.model.processed_tweet import ProcessedTweet
from src.model.tweet import Tweet


# from src.model.processed_tweet import ProcessedTweet

class RawTweetProcessor():
    def __init__(self):
        nltk.download('stopwords')

    def gen_processed_user_tweets(self, screen_name: str, user_getter: UserGetter, tweet_getter: UserTweetsGetter,
                                  user_processed_tweet_setter: UserProcessedTweetsSetter) -> None:
        """
        Assume that the input dao contains tweets associated with users.
        The common format is: {[Tweet object]}.
        Return and store processed user tweets.
        Update user tweet database to reflect processed tweet state.
        """
        assert (type(screen_name) is str)
        user_id = user_getter.get_user_by_screen_name(screen_name).id
        all_user_tweets = tweet_getter.get_user_tweets(user_id)
        all_processed_tweets = []
        for tweet in all_user_tweets:
            processed_tweet = ProcessedTweet.fromTweet(tweet)
            all_processed_tweets.append(processed_tweet)
        user_processed_tweet_setter.store_processed_tweets(user_id, all_processed_tweets)

    def gen_processed_tweets(self, tweet_getter: UserTweetsGetter, user_processed_tweet_setter: UserProcessedTweetsSetter) -> None:
        """
        Assume that the input dao contains tweets associated with users.
        The common format is: {[Tweet object]}.
        Return and store processed user tweets.
        Update user tweet database to reflect processed tweet state.
        """
        all_tweets_dict = tweet_getter.get_all_tweets_dict()

        for user_id in all_tweets_dict:
            all_user_tweets = all_tweets_dict[user_id]
            all_user_processed_tweets = []
            for tweet in all_user_tweets:
                processed_tweet = ProcessedTweet.fromTweet(tweet)
                all_user_processed_tweets.append(processed_tweet)
            user_processed_tweet_setter.store_processed_tweets(user_id, all_user_processed_tweets)

    def _process_tweet_text(self, tweet_text: str):  # -> ProcessedTweet:
        """
        Processes a given tweet text

        @param tweet the raw, unprocessed tweet text
        @return the processed tweet
        """
        text = tweet_text.lower()

        # Filter links, numbers, and emojis
        text = re.sub(r"\bhttps:\S*\b", "", text)
        text = re.sub(r"\b\d*\b", "", text)
        text = re.sub(r"[^\w\s@#]", "", text)

        processed_text_list = text.split()
        # Hashtags, usernames
        for i in range(0, len(processed_text_list)):
            word = processed_text_list[i]
            if '#' in word or '@' in word:
                processed_text_list[i] = ''

        processed_text_list = list(filter(lambda x: x != '', processed_text_list))

        # Run stemming: it's important to run this first before stop words for cases such as that's
        sno = nltk.stem.SnowballStemmer('english')
        processed_text_list = [sno.stem(word) for word in processed_text_list]

        # Remove stop words
        stopwords = set(nltk.corpus.stopwords.words('english'))
        stopwords.add('amp')
        for word in stopwords:
            if word in processed_text_list:
                # extract
                while (processed_text_list.count(word)):
                    processed_text_list.remove(word)

        return processed_text_list
