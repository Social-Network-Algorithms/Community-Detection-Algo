from typing import List

from src.model.processed_tweet import ProcessedTweet


class UserProcessedTweetsGetter:
    def get_user_processed_tweets(self, user_id: str) -> List[ProcessedTweet]:
        raise NotImplementedError("Subclasses should implement this")

    def get_all_processed_tweets(self) -> List[ProcessedTweet]:
        raise NotImplementedError("Subclasses should implement this")
