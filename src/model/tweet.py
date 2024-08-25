from typing import Dict, Optional
import json
from atproto_client.models import AppBskyFeedGetAuthorFeed, AppBskyFeedDefs, AppBskyEmbedRecord


class Tweet:
    """
    A class to represent a tweet
    """

    def __init__(self, id: str, user_id: str, created_at: str, text: str,
                 lang: str, retweet_id: Optional[str],
                 retweet_user_id: Optional[str], quote_id: Optional[str],
                 quote_user_id: Optional[str]):
        """
        Default constructor for a tweet.
        Key = (id, user_id)

        @param id the tweet's unique id
        @param user_id the id of the user who tweeted the tweet
        @param created_at a date string representation of the date the tweet
            was created
        @param text the text of the tweet
        @param lang the language of the tweet
        @param retweet_id if the tweet is a retweet, this is the id of the
            original tweet, otherwise it is None
        @param retweet_user_id if the tweet is a retweet, this is the user
            id of the original tweet's tweeter, otherwise it is None
        @param quote_id if the tweet is a quote, this is the id of the
            original tweet, otherwise it is None
        @param quote_user_id if the tweet is a quote, this is the user id of the
            original tweet's tweeter, otherwise it is None
        """
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.text = text
        self.lang = lang
        self.retweet_id = retweet_id
        self.retweet_user_id = retweet_user_id
        self.quote_id = quote_id
        self.quote_user_id = quote_user_id

    def toJSON(self) -> str:
        """
        Returns a json corresponding to the given tweet object

        @return a json representation of the tweet
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
            indent=4)

    def fromJSON(json_in: str):
        """
        Given a json representation of a tweet, returns the tweet object

        @param json_in the json to convert to a Tweet

        @return the Tweet object
        """
        obj = json.loads(json_in)
        tweet = Tweet(
            obj.get("id"),
            obj.get("user_id"),
            obj.get("created_at"),
            obj.get("text"),
            obj.get("lang"),
            obj.get("retweet_id"),
            obj.get("retweet_user_id"),
            obj.get("quote_id"),
            obj.get("quote_user_id"))

        return tweet

    def fromDict(dict: Dict):
        tweet = Tweet(dict["id"], dict["user_id"], dict["created_at"],
                      dict["text"], dict["lang"], dict["retweet_id"],
                      dict["retweet_user_id"], dict["quote_id"], dict["quote_user_id"])

        return tweet

    def fromTweepyJSON(json_in: Dict):
        """
        Given a json representation of a tweet returned by Tweepy, returns the
        tweet object

        @param json_in the json to convert to a Tweet

        @return the Tweet object
        """
        id = json_in.get("id")
        user_id = json_in.get("user").get("id")
        created_at = json_in.get("created_at")
        text = json_in.get("text")
        lang = json_in.get("lang")

        retweet_id = json_in.get("retweeted_status").get("id") \
            if json_in.get("retweeted_status") is not None \
            else None
        retweet_user_id = json_in.get("retweeted_status").get("user").get("id") \
            if json_in.get("retweeted_status") is not None \
            else None
        quote_id = json_in.get("quoted_status").get("id") \
            if json_in.get("quoted_status") is not None \
            else None
        quote_user_id = json_in.get("quoted_status").get("user").get("id") \
            if json_in.get("quoted_status") is not None \
            else None

        tweet = Tweet(id=id, user_id=user_id, created_at=created_at, text=text,
                      lang=lang, retweet_id=retweet_id, retweet_user_id=retweet_user_id,
                      quote_id=quote_id, quote_user_id=quote_user_id)

        return tweet

    def getAttributesFromATproto(post: AppBskyFeedGetAuthorFeed.Response,
                                 reason: Optional[AppBskyFeedDefs.ReasonRepost]):
        id = post.uri
        text = post.record.text
        lang = post.record.langs[0] \
            if post.record.langs is not None and len(post.record.langs) != 0 \
            else None

        if reason is not None:
            # repost
            # If the post is a repost, set the main and original user accordingly.
            retweet_id = post.uri
            retweet_user_id = post.author.did
            user_id = reason.by.did
            user_name = reason.by.handle
            created_at = reason.indexed_at
            quote_id, quote_user_id = None, None
        elif post["embed"] is not None and isinstance(post.embed, AppBskyEmbedRecord.ViewRecord):
            # quote
            quote_id = post.embed.record.uri
            quote_user_id = post.embed.record.author.did
            user_id = post.author.did
            user_name = post.author.handle
            created_at = post.indexed_at
            retweet_id, retweet_user_id = None, None

        else:
            # regular post
            user_id = post.author.did
            user_name = post.author.handle
            created_at = post.indexed_at
            retweet_id, retweet_user_id, quote_id, quote_user_id = None, None, None, None

        return id, user_id, user_name, created_at, text, lang, retweet_id, retweet_user_id, quote_id, quote_user_id

    def fromATprotoToObject(post: AppBskyFeedGetAuthorFeed.Response, reason: Optional[AppBskyFeedDefs.ReasonRepost]):
        """
        Given a AppBskyFeedGetAuthorFeed.Response object of a post returned by AT proto, returns the
        tweet object

        @return the Tweet object
        """
        id, user_id, user_name, created_at, text, lang, retweet_id, retweet_user_id, quote_id, quote_user_id = \
            Tweet.getAttributesFromATproto(post, reason)

        tweet = Tweet(id=id, user_id=user_id, created_at=created_at, text=text,
                      lang=lang, retweet_id=retweet_id, retweet_user_id=retweet_user_id,
                      quote_id=quote_id, quote_user_id=quote_user_id)

        return tweet

    def fromATprotoToJSON(post: AppBskyFeedGetAuthorFeed.Response, reason: Optional[AppBskyFeedDefs.ReasonRepost]):
        """
        Given a AppBskyFeedGetAuthorFeed.Response object of a post returned by AT proto, returns the
        JSON object

        @return the JSON object
        """
        id, user_id, user_name, created_at, text, lang, retweet_id, retweet_user_id, quote_id, quote_user_id = \
            Tweet.getAttributesFromATproto(post, reason)

        return {'id': id, 'user_id': user_id, 'user_name': user_name, 'created_at': created_at, 'text': text,
                'lang': lang,
                'retweet_id': retweet_id, 'retweet_user_id': retweet_user_id, 'quote_id': quote_id,
                'quote_user_id': quote_user_id}

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
