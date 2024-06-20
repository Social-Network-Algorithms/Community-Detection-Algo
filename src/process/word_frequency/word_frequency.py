from collections import Counter
from copy import copy
from typing import List

from src.dao.user_processed_tweets.getter.user_processed_tweets_getter import UserProcessedTweetsGetter
from src.model.processed_tweet import ProcessedTweet


class WordFrequency():
    """
    A class that contains all data processing functions involved in Word frequency.
    """
    def gen_global_word_count_vector(self, user_processed_tweets_getter: UserProcessedTweetsGetter):
        """
        Generate the global word count vector.
        Assume that the input dao contains tweets.
        The common format is a list of words from the tweets.

        @param user_processed_tweets_getter: a processed tweet mongo GetDAO
        @return: store the global word count vector format, with format: {word: num_times_used}
        """
        processed_tweets = user_processed_tweets_getter.get_all_processed_tweets()
        global_wc_vector = self._process_global_word_count_vector(processed_tweets)
        return global_wc_vector

    def gen_user_word_count_vector(self, user_processed_tweets_getter):
        """
        Generate the word count vector of specific user.
        Assume that the input dao contains tweets for users.
        The common format is a {user: [words from user's tweets]}.

        @param user_processed_tweets_getter: a processed tweet mongo GetDAO
        @return: store the user's global word count vector format, with format: user: {word: num_times_used}}
        """
        processed_tweets = user_processed_tweets_getter.get_all_processed_tweets()
        user_wc_vector = self._process_user_word_count_vector(processed_tweets)
        return user_wc_vector

    def gen_global_word_frequency_vector(self, user_processed_tweets_getter, wf_setter):
        """
        Generate the global word frequency.
        Assume that the input dao contains the global word count vector.
        The common format is {word: num_times_used}.

        @param user_processed_tweets_getter: a processed tweet mongo GetDAO
        @param wf_setter: a Word Frequency SetDAO
        @return: store and return the global word frequency vector, with the format {word: gwf}.
        """
        global_wc_vector = self.gen_global_word_count_vector(user_processed_tweets_getter)
        global_wf_vector = self._process_global_word_frequency_vector(global_wc_vector)
        wf_setter.store_global_word_frequency_vector(global_wf_vector)
        return global_wf_vector

    def gen_user_word_frequency_vector(self, user_processed_tweets_getter, wf_setter):
        """
        Generate the word frequency of a specific user.
        Assume that the input dao contains the user word count vector.
        The common format is {user: {word: num_times_used}}.

        @param user_processed_tweets_getter
        @param wf_setter: a Word Frequency SetDAO
        @return: store and return the user's global word frequency vector, with the format {user: {word: uwf}}.
        """

        user_wc_vector = self.gen_user_word_count_vector(user_processed_tweets_getter)
        user_wf_vector = self._process_user_word_frequency_vector(user_wc_vector)
        for user_id in user_wf_vector:
            wf_setter.store_user_word_frequency_vector(user_id, user_wf_vector[user_id])

        return user_wf_vector

    def gen_relative_user_word_frequency_vector(self, global_wf_getter, user_wf_getter, user_rwf_setter, user_processed_tweets_getter):
        """
        Generate the relative word frequency of a specific user.
        Assume that the input dao contains the global and user word frequency vectors.
        The common format is the global and user word frequency vectors specified previously.

        @param global_wf_getter: a global Word Frequency GetDAO
        @param user_wf_getter: a user Word Frequency SetDAO
        @param user_rwf_getter: a user Relative Word Frequency getDAO
        @param user_processed_tweets_getter
        @return: store and return the user's relative global word frequency vector,
        with the format {user: {word: ruwf}}.
        """
        global_wf_vector = global_wf_getter.get_global_word_frequency()
        user_wf_vector = user_wf_getter.get_all_user_word_frequencies()
        user_to_wcv = self.gen_user_word_count_vector(user_processed_tweets_getter)
        relative_user_wf_vector = self._process_relative_user_word_frequency_vector(global_wf_vector,
                                                                                    user_wf_vector,
                                                                                    user_to_wcv)
        for user_id in relative_user_wf_vector:
            user_rwf_setter.store_relative_user_word_frequency_vector(user_id, relative_user_wf_vector[user_id])

        return relative_user_wf_vector

    def _process_global_word_count_vector(self, tweets: List[ProcessedTweet]):
        """
        Count the number of each word in the word list.

        @param tweets: the list of processed tweets
        @return: the number of each word in the words
        """
        word_freq_vector = Counter()

        for tweet in tweets:
            text_dict = tweet.text
            for word in text_dict:
                word_freq_vector[word] += text_dict[word]

        return word_freq_vector

    def _process_user_word_count_vector(self, tweets: List[ProcessedTweet]):
        """
        Count the number of words of specific users.

        @param user_to_tweet_word_list: a list containing word list for each user.
        @return: the number of words of specific users.
        """
        user_wc_vector = {}
        for tweet in tweets:
            user = tweet.user_id
            text_dict = tweet.text
            counter = Counter()
            for word in text_dict:
                counter[word] += text_dict[word]

            if user not in user_wc_vector:
                user_wc_vector[user] = counter
            else:
                user_wc_vector[user] += counter

        return user_wc_vector

    def _process_global_word_frequency_vector(self, global_wc_vector):
        """
        Generate the word frequency by gwf = global_count/total_global_count.

        @param global_wc_vector: the generated global word vector
        @return: the word frequency of the global word vector
        """

        total_global_count = sum([global_wc_vector[word] for word in global_wc_vector])

        for word in global_wc_vector:
            global_wc_vector[word] /= float(total_global_count)

        return global_wc_vector

    def _process_user_word_frequency_vector(self, user_wc_vector):
        """
        Generate the word frequency of the user by uwf = user_count/total_user_count

        @param user_wc_vector: the generated user word vector
        @return: the word frequency of the user word vector
        """

        return {user:self._process_global_word_frequency_vector(user_wc_vector[user])
                for user in user_wc_vector}

    def _process_relative_user_word_frequency_vector(self, global_wf_vector, user_wf_vector, user_to_wcv):
        """
        Generate the relative word frequency of the users by rwf = uwf/gwf
        If a user word does not appear in the global count, then global_count = local_count.

        @param global_wf_vector: global word frequency vector
        @param user_wf_vector: global word frequency vector of the users
        @param user_to_wcv: global count vector of the users
        """

        relative_uwf_vector = {}
        local_community_cache = {}

        for user in user_wf_vector:
            relative_wf_vector = copy(user['word_frequency_vector'])

            for word in relative_wf_vector:
                global_count = global_wf_vector[word] if word in global_wf_vector else 0

                if global_count == 0:
                    # we can cache local community count
                    if word not in local_community_cache:
                        local_community_count = 0
                        for user_ in user_to_wcv:
                            u_word_counter = user_to_wcv["relative_word_frequency_vector"]
                            if word in u_word_counter:
                                local_community_count += u_word_counter[word]
                        local_community_cache[word] = local_community_count
                    else:
                        local_community_count = local_community_cache[word]
                    global_count = local_community_count

                relative_wf_vector[word] /= float(global_count)

            relative_uwf_vector[user['user_id']] = relative_wf_vector

        return relative_uwf_vector
