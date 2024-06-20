from typing import Dict, Union, Optional
import json
from atproto_client.models import AppBskyActorDefs


class User:
    """
    A class that represents a twitter user
    """

    def __init__(self, id: str, screen_name: str, name: str, created_at: str,
                 followers_count: int, friends_count: int, listed_count: int,
                 favourites_count: int, statuses_count: int, default_profile: bool,
                 default_profile_image: bool):
        """
        Constructor for a User object

        @param id the unique id of the twitter user
        @param screen_name the screen name of the twitter user
        @param name the name of the twitter user
        @param created_at the date the twitter user was created
        @param followers_count the number of followers of the twitter user
        @param friends_count the number of friends of the twitter user
        @param listed_count the number of lists the user is a part of
        @param favourites_count the number of tweets this user has liked
        @param statuses_count the number of tweets the user has tweeted
            (including retweets)
        @param default_profile a boolean that is true iff the user has not
            edited their theme or background
        @param default_profile_image a boolean that is true iff the user has
            not edited their profile image
        """
        self.id = id
        self.screen_name = screen_name
        self.name = name
        self.created_at = created_at
        self.followers_count = followers_count
        self.friends_count = friends_count
        self.listed_count = listed_count
        self.favourites_count = favourites_count
        self.statuses_count = statuses_count
        self.default_profile = default_profile
        self.default_profile_image = default_profile_image

    def fromJSON(json_in: str):
        """
        Given a json representation of a tweet, returns the user object

        @param json_in the json to convert to a User

        @return the User object
        """
        obj = json.loads(json_in)
        user = User(
            obj.get("id"),
            obj.get("screen_name"),
            obj.get("name"),
            obj.get("created_at"),
            obj.get("followers_count"),
            obj.get("friends_count"),
            obj.get("listed_count"),
            obj.get("favourites_count"),
            obj.get("statuses_count"),
            obj.get("default_profile"),
            obj.get("default_profile_image"))

        return user

    def fromDict(dict: Dict):
        if dict is None:
            return None
        user = User(dict["id"], dict["screen_name"], dict["name"],
                    dict["created_at"], dict["followers_count"], dict["friends_count"],
                    dict["listed_count"], dict["favourites_count"],
                    dict["statuses_count"], dict["default_profile"],
                    dict["default_profile_image"])

        return user

    def fromTweepyJSON(json_in: Dict):
        """
        Given a json representation of a user returned by Tweepy, returns the
        user object

        @param json_in the json to convert to a User

        @return the User object
        """
        id = json_in.get("id")
        screen_name = json_in.get("screen_name")
        name = json_in.get("name")
        created_at = json_in.get("created_at")
        followers_count = json_in.get("followers_count")
        friends_count = json_in.get("friends_count")
        listed_count = json_in.get("listed_count")
        favourites_count = json_in.get("favourites_count")
        statuses_count = json_in.get("statuses_count")
        default_profile = json_in.get("default_profile")
        default_profile_image = json_in.get("default_profile_image")

        user = User(id=id, name=name, screen_name=screen_name,
                    created_at=created_at, followers_count=followers_count,
                    friends_count=friends_count, listed_count=listed_count,
                    favourites_count=favourites_count, statuses_count=statuses_count,
                    default_profile=default_profile,
                    default_profile_image=default_profile_image)

        return user

    def fromATprotoObject(profile: AppBskyActorDefs.ProfileViewDetailed):
        """
        Given a ProfileViewDetailed representation of a user returned by AT proto, returns the
        user object

        @param json_in the json to convert to a User

        @return the User object
        """
        id = profile.did
        screen_name = profile.handle
        name = profile.display_name
        created_at = profile.indexed_at
        followers_count = profile.followers_count
        friends_count = profile.follows_count
        listed_count = profile.associated.lists
        favourites_count = 0
        statuses_count = profile.posts_count
        default_profile = False
        default_profile_image = False

        user = User(id=id, name=name, screen_name=screen_name,
                    created_at=created_at, followers_count=followers_count,
                    friends_count=friends_count, listed_count=listed_count,
                    favourites_count=favourites_count, statuses_count=statuses_count,
                    default_profile=default_profile,
                    default_profile_image=default_profile_image)

        return user

    def toJSON(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def get_id(self):
        return self.id

    def __str__(self):
        return str(self.__dict__)
