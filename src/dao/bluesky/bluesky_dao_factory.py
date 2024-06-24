from typing import Dict
from src.dao.bluesky.bluesky_dao import BlueSkyGetter
from src.dao.bluesky.atproto_bluesky_dao import TweepyBlueSkyGetter

class BlueskyDAOFactory():
    def create_getter(download_source: Dict) -> BlueSkyGetter:
        bluesky_getter = None
        if download_source["type"] == "Tweepy":
            bluesky_getter = TweepyBlueSkyGetter()
        else:
            raise Exception("Datastore type not supported")

        return bluesky_getter
