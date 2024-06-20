from copy import deepcopy

from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.shared.logger_factory import LoggerFactory

log = LoggerFactory.logger(__name__)

class ExtendedFriendsCleaner():
    def __init__(self, user_friends_getter, cleaned_user_friends_setter, user_getter, user_tweets_getter: UserTweetsGetter,
                 consumption_ranker, retweets_ranker):
        self.user_friends_getter = user_friends_getter
        self.cleaned_user_friends_setter = cleaned_user_friends_setter
        self.user_getter = user_getter
        self.user_tweets_getter = user_tweets_getter
        self.consumption_ranker = consumption_ranker
        self.retweets_ranker = retweets_ranker

    def clean_friends(self, user_id, tweet_threshold=50, follower_threshold=50, friend_threshold=0,
                      bot_threshold=0, local_follower=0,
                      local_following=10, consumption_threshold=20, production_threshold=50):
        friends_list = self.user_friends_getter.get_user_friends_ids(user_id)
        clean_friends_1 = self.clean_friends_global(user_id, tweet_threshold, follower_threshold,
                                                    friend_threshold, bot_threshold)
        final = self.clean_friends_local(user_id, clean_friends_1, local_follower, local_following)
        return final

    def clean_friends_global(self, user_id, tweet_threshold=50, follower_threshold=50, friend_threshold=0,
                             bot_threshold=0):
        friends_list = self.user_friends_getter.get_user_friends_ids(user_id)
        clean_friends_list = []
        clean_users = []
        for id in friends_list:
            user = self.user_getter.get_user_by_id(id)
            if user is None:
                log.info("Removed user " + str(id) + " because they couldn't be downloaded")
                continue
            #elif user.followers_count < follower_threshold:
                #log.info("Removed user " + str(id) + " because they have " + str(user.followers_count) + " followers")
                #continue
            elif len(self.user_tweets_getter.get_tweets_by_user_id_time_restricted(user_id)) < tweet_threshold:
                log.info("Removed user " + str(id) + " because they have " + str(user.statuses_count) + " tweets")
                continue
            #elif user.friends_count < friend_threshold:
                #log.info(f"Removed user {id} because they have {user.friends_count} friends")
                #continue
            elif user.followers_count < bot_threshold * user.friends_count:
                log.info("Removed user " + str(id) + " because they have " + str(bot_threshold) + " times as many followers as people who they follow")
                continue
            else:
                clean_friends_list.append(id)
                clean_users.append(user)

        log.info("original friends: " + str(len(friends_list)) + " remaining friends: " + str(len(clean_friends_list)))

        if self.cleaned_user_friends_setter is not None:
            self.cleaned_user_friends_setter.store_friends(user_id, clean_friends_list)

        return clean_friends_list

    def clean_friends_global_by_percentage(self, user_id, friends_list, tweet_percent=60, follower_percent=60, bot_threshold=0.5,
                                           check_profile_picture=False):
        clean_friends_list = []
        users = []

        tweets = []
        followers = []
        target_tweet = int(len(friends_list) * (tweet_percent/100))
        target_follower = int(len(friends_list) * (follower_percent/100))

        for id in friends_list:
            user = self.user_getter.get_user_by_id(id)
            if user is None:
                log.info("Removed user " + str(id) + " because they couldn't be downloaded")
                continue
            users.append(user)
            tweets.append(user.statuses_count)
            followers.append(user.followers_count)

        tweets.sort(reverse=True)
        followers.sort(reverse=True)
        tweet_threshold = tweets[target_tweet-1]
        follower_threshold = followers[target_follower-1]

        for user in users:
            id = user.id
            if user.followers_count < follower_threshold:
                #log.info("Removed user " + str(id) + " because they have " + str(user.followers_count) + " followers")
                continue
            elif user.statuses_count < tweet_threshold:
                #log.info("Removed user " + str(id) + " because they have " + str(user.statuses_count) + " tweets")
                continue
            elif user.followers_count < bot_threshold * user.friends_count:
                #log.info("Removed user " + str(id) + " because they have " + str(bot_threshold) + " times as many followers as people who they follow")
                continue
            elif check_profile_picture and user.default_profile_image:
                #log.info("Removed user " + str(id) + " because they have default profile picture")
                continue
            else:
                clean_friends_list.append(id)

        log.info("original friends: " + str(len(friends_list)) + " remaining friends: " + str(len(clean_friends_list)))

        if self.cleaned_user_friends_setter is not None:
            self.cleaned_user_friends_setter.store_friends(user_id, clean_friends_list)

        return clean_friends_list

    def clean_friends_local(self, user_id, friends_list, local_follower=0, local_following=10):
        clean_friends_list = deepcopy(friends_list)
        deleted_friends = []
        clean = False
        user_friends = {}
        for user in friends_list:
            friends = self.user_friends_getter.get_user_friends_ids(str(user))
            user_friends[user] = set(friends)
        while not clean:
            new_friends = []
            set_clean_friends = set(clean_friends_list)
            for user in clean_friends_list:
                friends = user_friends[user]
                # TODO: maybe also clean by followers
                if len(set_clean_friends.intersection(friends)) >= local_following:
                    new_friends.append(user)
                else:
                    deleted_friends.append(user)
            if new_friends == clean_friends_list:
                clean = True
            else:
                clean_friends_list = new_friends
            log.info('iteration!')

        # if 254201259 not in clean_friends_list:
        #     clean_friends_list.append(254201259)
        # log.info("merbroussard's local following count")
        # log.info(len(set(clean_friends_list).intersection(user_friends[254201259])))
        # log.info([self.user_getter.get_user_by_id(id).screen_name for
        #           id in set(clean_friends_list).intersection(user_friends[254201259])])

        log.info("original friends: " + str(len(friends_list)) + " remaining friends: " + str(len(clean_friends_list)))

        if self.cleaned_user_friends_setter is not None:
            self.cleaned_user_friends_setter.store_friends(user_id, clean_friends_list)
        # return user_friends[254201259]
        return clean_friends_list, deleted_friends

    def clean_friends_rankings(self, user_id, friends_list, consumption_threshold, production_threshold): # Clean by rankings
        # thresholds are percentage to keep

        consumption = self.consumption_ranker.score_users(friends_list)
        ranked_consumption = list(sorted(consumption, key=consumption.get, reverse=True))
        production = self.retweets_ranker.score_users(friends_list)
        ranked_production = list(sorted(production, key=production.get, reverse=True))

        consumption_target = int(len(friends_list) * (consumption_threshold/100))
        production_target = int(len(friends_list) * (production_threshold/100))
        clean_friends_list = []

        for id in friends_list:
            if ranked_consumption.index(id) > consumption_target:
                log.info("Removed user " + str(id) + " for low consumption utility")
                continue
            elif ranked_production.index(id) > production_target:
                log.info("Removed user " + str(id) + " for low production utility")
                continue
            else:
                clean_friends_list.append(id)

        log.info("original friends: " + str(len(friends_list)) + " remaining friends: " + str(len(clean_friends_list)))

        if self.cleaned_user_friends_setter is not None:
            self.cleaned_user_friends_setter.store_friends(user_id, clean_friends_list)

        return clean_friends_list
