from src.dao.bluesky.bluesky_dao import BlueSkyGetter
from src.dao.user.setter.user_setter import UserSetter
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

class BlueskyUserDownloader():
    """
    Downloads a bluesky User
    """

    def __init__(self, bluesky_getter: BlueSkyGetter, user_setter: UserSetter):
        self.bluesky_getter = bluesky_getter
        self.user_setter = user_setter

    def download_user_by_screen_name(self, screen_name: str):
        log.debug("calling bluesky getter with screen name %s" % screen_name)
        user = self.bluesky_getter.get_user_by_screen_name(screen_name)
        log.debug("storing user %s" % (str(user.screen_name)))
        self.user_setter.store_user(user)

    def download_user_by_id(self, user_id: str):
        log.debug("calling bluesky getter with user id %s" % (str(user_id)))
        user = self.bluesky_getter.get_user_by_id(user_id)
        log.debug("storing user %s" % (str(user.screen_name)))
        self.user_setter.store_user(user)
