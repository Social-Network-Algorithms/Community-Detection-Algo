import nltk
import re
import datetime
from typing import Dict, List, Union, Optional
from src.model.tweet import Tweet
from src.model.word_frequency_vector import WordFrequencyVector
import json
import datetime

class Processor():
    def __init__(self):
        # Remove stop words
        stopwords = set(nltk.corpus.stopwords.words('english'))
        stopwords.add('amp')

        sno = nltk.stem.SnowballStemmer('english')

        self.stopwords = stopwords
        self.sno = sno


PROCESSOR = Processor()
class ProcessedTweet:
    """
    A class to represent a processed tweet
    """
    def __init__(self, id: str, user_id: str, text: Dict):
        """
        Default constructor for a processed tweet

        @param the id of the tweet
        @param user_id the id of the user who tweeted the tweet
        @param text a dictionary containing the word count of each word, not
            including words that have been removed
        """
        self.id = id
        self.user_id = user_id
        self.text = text
        self.wf_vector = WordFrequencyVector.fromDict(text)

    def toDict(self) -> Dict:
        dict = {}

        dict["id"] = self.id
        dict["user_id"] = self.user_id
        dict["text"] = self.text

        return dict

    def fromDict(dict: Dict):
        processed_tweet = ProcessedTweet(
            dict["id"],
            dict["user_id"],
            dict["text"]
        )

        return processed_tweet

    def toJSON(json_in: str) -> str:
        """
        Returns a json corresponding to the given processed tweet object

        @returns a json representation of the processed tweet
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
            indent=4)

    def fromJSON(json_in: str):
        """
        Given a json representation of a processed tweet, returns the processed
        tweet, returns the processed tweet object
        """
        obj = json.loads(json_in)
        processed_tweet = ProcessedTweet(
            obj.get("id"),
            obj.get("user_id"),
            obj.get("text")
        )

        return processed_tweet

    def fromTweet(tweet: Tweet):
        """
        Given a tweet, return the processed tweet
        """
        id = tweet.id
        user_id = tweet.user_id
        raw_text = tweet.text
        text = ProcessedTweet.process_tweet_text(raw_text)

        processed_tweet = ProcessedTweet(
            id,
            user_id,
            text
        )

        return processed_tweet

    def process_tweet_text(text: str) -> Dict[str, int]:
        """
        Processes a given tweet

        @param tweet the raw, unprocessed tweet
        @return the processed tweet
        """
        text = text.lower()

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
        processed_text_list = [PROCESSOR.sno.stem(word) for word in processed_text_list]

        word_dict = {}

        for word in processed_text_list:
            if word not in PROCESSOR.stopwords:
                if word in word_dict:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1

        return word_dict

    def get_word_frequency_vector(self):
        return self.wf_vector

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
