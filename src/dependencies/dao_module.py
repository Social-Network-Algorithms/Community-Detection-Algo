from src.dao.cluster.cluster_dao_factory import ClusterDAOFactory
from src.dao.local_neighbourhood.local_neighbourhood_dao_factory import LocalNeighbourhoodDAOFactory
from src.dao.processed_tweet.processed_tweet_dao_factory import ProcessedTweetDAOFactory
from src.dao.ranking.ranking_dao_factory import RankingDAOFactory
from src.dao.social_graph.social_graph_dao_factory import SocialGraphDAOFactory
from src.dao.bluesky.bluesky_dao_factory import BlueskyDAOFactory
from src.dao.user.user_dao_factory import UserDAOFactory
from src.dao.user_follower.user_follower_dao_factory import UserFollowerDAOFactory
from src.dao.user_friend.user_friend_dao_factory import UserFriendDAOFactory
from src.dao.user_processed_tweets.user_processed_tweets_dao_factory import UserProcessedTweetsDAOFactory
from src.dao.user_tweets.user_tweets_dao_factory import UserTweetsDAOFactory
from src.dao.user_word_frequency.user_word_frequency_dao_factory import UserWordFrequencyDAOFactory
from src.dao.user_relative_word_frequency.user_relative_word_frequency_dao_factory import UserRelativeWordFrequencyDAOFactory
from src.dao.cluster_word_frequency.cluster_word_frequency_dao_factory import ClusterWordFrequencyDAOFactory
from src.dao.cluster_relative_word_frequency.cluster_relative_word_frequency_dao_factory import ClusterRelativeWordFrequencyDAOFactory
from src.dao.global_word_frequency.global_word_frequency_dao_factory import GlobalWordFrequencyDAOFactory
from src.dao.community.community_dao_factory import CommunityDAOFactory
from src.dao.retweeted_users.retweeted_users_dao_factory import RetweetedUsersDAOFactory
from src.dao.local_neighbourhood_from_RT_users.LN_from_RT_users_dao_factory import LNFromRTUsersDAOFactory
from src.dao.user_activity.user_activity_dao_factory import UserActivityDAOFactory
from src.dao.local_neighbourhood_from_RT_ids.LN_from_RT_ids_dao_factory import LNFromRTIdsDAOFactory


class DAOModule():
    def __init__(self, config):
        input_datastore = config.get("input-datastore", {})
        output_datastore = config.get("output-datastore", {})
        inout_datastore = config.get("inout-datastore", {})

        # Set input datastore to be the union of input and inout
        # (with inout taking priority)
        self.input_datastore = input_datastore
        self.input_datastore.update(inout_datastore)

        # Set output datastore to be the union of output and inout
        # (with inout taking priority)
        self.output_datastore = output_datastore
        self.output_datastore.update(inout_datastore)

    def get_user_activity_getter(self, user_activity: str):
        if user_activity == 'friends':
            return UserActivityDAOFactory.create_getter(self.get_user_friend_getter(), user_activity)
        elif user_activity == 'user retweets':
            return UserActivityDAOFactory.create_getter(self.get_retweeted_users_getter(), user_activity)
        elif user_activity == 'user retweets ids':
            return UserActivityDAOFactory.create_getter(self.get_user_tweets_getter(), user_activity)

    def get_bluesky_getter(self):
        return BlueskyDAOFactory.create_getter(
            self.input_datastore["Download-Source"])

    def get_cluster_getter(self):
        return ClusterDAOFactory.create_getter(
            self.input_datastore["Cluster"])

    def get_cluster_setter(self):
        return ClusterDAOFactory.create_setter(
            self.output_datastore["Cluster"])
         
    def get_local_neighbourhood_getter(self, user_activity: str):
        if user_activity == 'friends':
            return LocalNeighbourhoodDAOFactory.create_getter(
            self.input_datastore["LocalNeighbourhood"])
        elif user_activity == 'user retweets':
            return LNFromRTUsersDAOFactory.create_getter(
            self.input_datastore["LocalNeighbourhoodsFromRTUsers"])
        elif user_activity == 'user retweets ids':
            return LNFromRTIdsDAOFactory.create_getter(
            self.input_datastore["LocalNeighbourhoodsFromRTIds"])

    def get_local_neighbourhood_setter(self, user_activity: str):
        if user_activity == 'friends':
            return LocalNeighbourhoodDAOFactory.create_setter(
            self.output_datastore["LocalNeighbourhood"])
        elif user_activity == 'user retweets':
            return LNFromRTUsersDAOFactory.create_setter(
            self.output_datastore["LocalNeighbourhoodsFromRTUsers"])
        elif user_activity == 'user retweets ids':
            return LNFromRTIdsDAOFactory.create_setter(
            self.output_datastore["LocalNeighbourhoodsFromRTIds"])

    def get_processed_tweet_getter(self):
        return ProcessedTweetDAOFactory.create_getter(
            self.input_datastore["ProcessedTweet"])

    def get_processed_tweet_setter(self):
        return ProcessedTweetDAOFactory.create_setter(
            self.output_datastore["ProcessedTweet"])

    def get_ranking_getter(self):
        return RankingDAOFactory.create_getter(
            self.input_datastore["Ranking"])

    def get_ranking_setter(self):
        return RankingDAOFactory.create_setter(
            self.output_datastore["Ranking"])

    def get_user_tweets_getter(self):
        return UserTweetsDAOFactory.create_getter(
            self.input_datastore["UserTweet"])

    def get_user_tweets_setter(self):
        return UserTweetsDAOFactory.create_setter(
            self.output_datastore["UserTweet"])

    def get_user_processed_tweets_getter(self):
        return UserProcessedTweetsDAOFactory.create_getter(
            self.input_datastore["UserProcessedTweet"])

    def get_user_processed_tweets_setter(self):
        return UserProcessedTweetsDAOFactory.create_setter(
            self.output_datastore["UserProcessedTweet"])

    def get_social_graph_getter(self):
        return SocialGraphDAOFactory.create_getter(
            self.input_datastore["SocialGraph"])

    def get_social_graph_setter(self):
        return SocialGraphDAOFactory.create_setter(
            self.output_datastore["SocialGraph"])

    def get_user_getter(self):
        return UserDAOFactory.create_getter(
            self.input_datastore["Users"])

    def get_user_setter(self):
        return UserDAOFactory.create_setter(
            self.output_datastore["Users"])

    # def get_user_follower_getter(self):
    #     return UserFollowerDAOFactory.create_getter(
    #         self.input_datastore["Followers"])

    def get_user_follower_setter(self):
        return UserFollowerDAOFactory.create_setter(
            self.output_datastore["Followers"])

    def get_retweeted_users_getter(self):
        return RetweetedUsersDAOFactory.create_getter(
            self.input_datastore["RetweetedUsers"])

    def get_retweeted_users_setter(self):
        return RetweetedUsersDAOFactory.create_setter(
            self.output_datastore["RetweetedUsers"])

    def get_user_friend_getter(self):
        return UserFriendDAOFactory.create_getter(
            self.input_datastore["Friends"])

    def get_user_friend_setter(self):
        return UserFriendDAOFactory.create_setter(
            self.output_datastore["Friends"])

    def get_cleaned_user_friend_getter(self):
        return UserFriendDAOFactory.create_getter(
            self.input_datastore["CleanedFriends"])

    def get_cleaned_user_friend_setter(self):
        return UserFriendDAOFactory.create_setter(
            self.output_datastore["CleanedFriends"])

    def get_user_word_frequency_getter(self):
        return UserWordFrequencyDAOFactory.create_getter(
            self.input_datastore["UserWordFrequency"])

    def get_user_word_frequency_setter(self):
        return UserWordFrequencyDAOFactory.create_setter(
            self.output_datastore["UserWordFrequency"])

    def get_cluster_word_frequency_getter(self):
        return ClusterWordFrequencyDAOFactory.create_getter(
            self.input_datastore["ClusterWordFrequency"])

    def get_cluster_word_frequency_setter(self):
        return ClusterWordFrequencyDAOFactory.create_setter(
            self.output_datastore["ClusterWordFrequency"])

    def get_cluster_relative_word_frequency_getter(self):
        return ClusterRelativeWordFrequencyDAOFactory.create_getter(
            self.input_datastore["ClusterRelativeWordFrequency"])

    def get_cluster_relative_word_frequency_setter(self):
        return ClusterRelativeWordFrequencyDAOFactory.create_setter(
            self.output_datastore["ClusterRelativeWordFrequency"])

    def get_global_word_frequency_getter(self):
        return GlobalWordFrequencyDAOFactory.create_getter(
            self.input_datastore["GlobalWordFrequency"])

    def get_global_word_frequency_setter(self):
        return GlobalWordFrequencyDAOFactory.create_setter(
            self.output_datastore["GlobalWordFrequency"])

    def get_user_relative_word_frequency_getter(self):
        return UserRelativeWordFrequencyDAOFactory.create_getter(
            self.input_datastore["UserRelativeWordFrequency"])

    def get_user_relative_word_frequency_setter(self):
        return UserRelativeWordFrequencyDAOFactory.create_setter(
            self.output_datastore["UserRelativeWordFrequency"])

    def get_community_setter(self):
        return CommunityDAOFactory.create_setter(
            self.output_datastore["Community"])
