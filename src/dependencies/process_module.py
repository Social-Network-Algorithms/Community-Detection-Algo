from quality_tests.test_core_detection_correctness import TestCoreDetection
from quality_tests.test_existing_algs import TestExistingAlgs
from quality_tests.test_expansion_correctness import TestCoreExpansion
from quality_tests.test_final_community_insights import TestCommunityInsights
from src.process.community_expansion.community_expansion import CommunityExpansionAlgorithm
from src.process.community_expansion.core_refiner import CoreRefiner
from src.process.community_ranking.community_consumption_utility_ranker import CommunityConsumptionUtilityRanker
from src.process.community_ranking.community_production_utility_ranker import CommunityProductionUtilityRanker
from src.process.community_ranking.community_social_support_ranker import CommunitySocialSupportRanker
from src.process.data_analysis.dataset_creator import DatasetCreator
from src.process.ranking.relative_production_ranker import RelativeProductionRanker
from src.dependencies.dao_module import DAOModule
from src.process.clustering.clusterer_factory import ClustererFactory
from src.process.core_detection.core_detector_jaccard import JaccardCoreDetector
from src.process.download.follower_downloader import BlueskyFollowerDownloader
from src.process.download.friend_downloader import FriendDownloader
from src.process.download.local_neighbourhood_downloader import LocalNeighbourhoodDownloader
from src.process.download.local_neighbourhood_tweet_downloader import LocalNeighbourhoodTweetDownloader
from src.process.download.tweet_downloader import BlueskyTweetDownloader
from src.process.download.user_downloader import BlueskyUserDownloader
from src.process.download.user_tweet_downloader import UserTweetDownloader
from src.process.ranking.consumption_utility_ranker import ConsumptionUtilityRanker
from src.process.ranking.social_support_ranker import SocialSupportRanker
from src.process.ranking.influence_one_ranker import InfluenceOneRanker
from src.process.ranking.influence_two_ranker import InfluenceTwoRanker
from src.process.ranking.followers_ranker import FollowerRanker
from src.process.ranking.local_followers_ranker import LocalFollowersRanker
from src.process.raw_tweet_processing.tweet_processor import TweetProcessor
from src.process.social_graph.social_graph_constructor import SocialGraphConstructor
from src.process.word_frequency.user_word_frequency_processor import UserWordFrequencyProcessor
from src.process.word_frequency.cluster_word_frequency_processor import ClusterWordFrequencyProcessor


class ProcessModule():
    """
    The process module is used to abstract the creation of processes, so they
    can be injected into classes which depend on them
    """

    def __init__(self, dao_module: DAOModule):
        self.dao_module = dao_module

    # Clustering
    def get_clusterer(self):
        social_graph_getter = self.dao_module.get_social_graph_getter()
        cluster_setter = self.dao_module.get_cluster_setter()
        user_friends_getter = self.dao_module.get_user_friend_getter()

        return ClustererFactory.create_clusterer(social_graph_getter, cluster_setter, user_friends_getter)

    def get_jaccard_core_detector(self, user_activity: str):
        user_getter = self.dao_module.get_user_getter()
        user_downloader = self.get_user_downloader()
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        user_friend_getter = self.dao_module.get_user_friend_getter()
        retweeted_users_getter = self.dao_module.get_retweeted_users_getter()
        sosu_ranker = self.get_ranker("SocialSupport")

        return JaccardCoreDetector(user_getter, user_downloader,
                                   user_tweets_getter, user_friend_getter, retweeted_users_getter, sosu_ranker)

    def get_dataset_creator(self, file_path):
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        friends_getter = self.dao_module.get_user_friend_getter()
        user_getter = self.dao_module.get_user_getter()
        return DatasetCreator(
            file_path,
            user_getter,
            user_tweets_getter,
            friends_getter)

    def get_core_refiner(self, initial_seed, dataset_creator: DatasetCreator):
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        friends_getter = self.dao_module.get_user_friend_getter()
        user_getter = self.dao_module.get_user_getter()
        retweeted_users_getter = self.dao_module.get_retweeted_users_getter()
        return CoreRefiner(initial_seed,
                           user_getter,
                           user_tweets_getter,
                           friends_getter,
                           retweeted_users_getter,
                           dataset_creator)

    def get_community_expansion(self, initial_seed, dataset_creator: DatasetCreator):
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        friends_getter = self.dao_module.get_user_friend_getter()
        user_getter = self.dao_module.get_user_getter()
        retweeted_users_getter = self.dao_module.get_retweeted_users_getter()
        return CommunityExpansionAlgorithm(
            initial_seed,
            user_getter,
            user_tweets_getter,
            friends_getter,
            retweeted_users_getter,
            dataset_creator)

    def get_community_quality_tests(self, initial_seed):
        user_getter = self.dao_module.get_user_getter()
        user_friend_getter = self.dao_module.get_user_friend_getter()
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        retweeted_users_getter = self.dao_module.get_retweeted_users_getter()
        community_social_support_ranker = CommunitySocialSupportRanker(user_tweets_getter, user_friend_getter,
                                                                       None)

        core_detection_correctness = TestCoreDetection(user_getter, retweeted_users_getter, user_friend_getter, community_social_support_ranker, initial_seed)
        core_expansion_correctness = TestCoreExpansion(user_getter, retweeted_users_getter, user_friend_getter, community_social_support_ranker, initial_seed)
        final_comm_insights = TestCommunityInsights(user_getter, retweeted_users_getter, user_friend_getter, community_social_support_ranker, initial_seed)
        # existing_algs = TestExistingAlgs(user_getter, retweeted_users_getter, user_friend_getter, community_social_support_ranker, initial_seed)
        return [core_detection_correctness, core_expansion_correctness, final_comm_insights]
        # return [core_detection_correctness, core_expansion_correctness, final_comm_insights, existing_algs]

    # Downloaduser_setter
    def get_follower_downloader(self):
        bluesky_getter = self.dao_module.get_bluesky_getter()
        user_follower_setter = self.dao_module.get_user_follower_setter()
        user_setter = self.dao_module.get_user_setter()

        follower_downloader = BlueskyFollowerDownloader(bluesky_getter, user_follower_setter,
                                                        user_setter)

        return follower_downloader

    def get_friend_downloader(self):
        bluesky_getter = self.dao_module.get_bluesky_getter()
        user_friend_getter = self.dao_module.get_user_friend_getter()
        user_friend_setter = self.dao_module.get_user_friend_setter()
        user_setter = self.dao_module.get_user_setter()
        user_getter = self.dao_module.get_user_getter()

        friend_downloader = FriendDownloader(bluesky_getter, user_friend_getter,
                                             user_friend_setter, user_setter, user_getter)

        return friend_downloader

    def get_local_neighbourhood_downloader(self, user_activity: str):
        bluesky_getter = self.dao_module.get_bluesky_getter()
        user_downloader = self.get_user_downloader()
        user_getter = self.dao_module.get_user_getter()
        user_activity_getter = self.dao_module.get_user_activity_getter(user_activity=user_activity)
        user_friend_getter = self.dao_module.get_user_friend_getter()
        user_friend_setter = self.dao_module.get_user_friend_setter()
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        retweeted_user_setter = self.dao_module.get_retweeted_users_setter()
        local_neighbourhood_setter = self.dao_module.get_local_neighbourhood_setter(user_activity=user_activity)

        local_neighbourhood_downloader = LocalNeighbourhoodDownloader(bluesky_getter, user_downloader,
                                                                      user_getter,
                                                                      user_friend_getter,
                                                                      user_activity_getter, user_friend_setter,
                                                                      user_tweets_getter,
                                                                      retweeted_user_setter,
                                                                      local_neighbourhood_setter,
                                                                      user_activity=user_activity)

        return local_neighbourhood_downloader

    def get_local_neighbourhood_tweet_downloader(self, user_activity: str):
        user_tweet_downloader = self.get_user_tweet_downloader()
        local_neighbourhood_getter = self.dao_module.get_local_neighbourhood_getter(user_activity=user_activity)

        local_neighbourhood_tweet_downloader = LocalNeighbourhoodTweetDownloader(user_tweet_downloader,
                                                                                 local_neighbourhood_getter)

        return local_neighbourhood_tweet_downloader

    def get_tweet_downloader(self):
        bluesky_getter = self.dao_module.get_bluesky_getter()
        user_tweets_setter = self.dao_module.get_user_tweets_setter()

        tweet_downloader = BlueskyTweetDownloader(
            bluesky_getter, user_tweets_setter)

        return tweet_downloader

    def get_user_downloader(self):
        bluesky_getter = self.dao_module.get_bluesky_getter()
        user_setter = self.dao_module.get_user_setter()

        user_downloader = BlueskyUserDownloader(bluesky_getter, user_setter)

        return user_downloader

    def get_user_tweet_downloader(self):
        bluesky_getter = self.dao_module.get_bluesky_getter()
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        user_tweets_setter = self.dao_module.get_user_tweets_setter()
        user_getter = self.dao_module.get_user_getter()

        user_tweet_downloader = UserTweetDownloader(bluesky_getter, user_tweets_getter, user_tweets_setter,
                                                    user_getter)

        return user_tweet_downloader

    # Ranking
    def get_ranker(self, type=None):
        bluesky_getter = self.dao_module.get_bluesky_getter()
        cluster_getter = self.dao_module.get_cluster_getter()
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        user_tweets_setter = self.dao_module.get_user_tweets_setter()
        ranking_setter = self.dao_module.get_ranking_setter()
        user_getter = self.dao_module.get_user_getter()
        friends_getter = self.dao_module.get_user_friend_getter()
        friends_setter = self.dao_module.get_user_friend_setter()

        if type == "Consumption":
            ranker = ConsumptionUtilityRanker(
                bluesky_getter, cluster_getter, user_tweets_getter, user_tweets_setter, user_getter, ranking_setter)
        elif type == "Follower":
            ranker = FollowerRanker(
                bluesky_getter, cluster_getter, user_getter, ranking_setter)
        elif type == "LocalFollowers":
            ranker = LocalFollowersRanker(
                bluesky_getter, cluster_getter, user_getter, friends_getter, ranking_setter)
        elif type == "RelativeProduction":
            ranker = RelativeProductionRanker(
                bluesky_getter, cluster_getter, user_tweets_getter, ranking_setter, user_getter)
        elif type == "InfluenceOne":
            ranker = InfluenceOneRanker(
                bluesky_getter, user_tweets_getter, user_tweets_setter, friends_getter, friends_setter, ranking_setter)
        elif type == "InfluenceTwo":
            ranker = InfluenceTwoRanker(
                bluesky_getter, user_tweets_getter, user_tweets_setter, friends_getter, friends_setter, ranking_setter)
        elif type == "SocialSupport":
            ranker = SocialSupportRanker(
                bluesky_getter, user_tweets_getter, user_tweets_setter, user_getter, friends_getter, friends_setter,
                ranking_setter)
        else:
            ranker = SocialSupportRanker(
                bluesky_getter, user_tweets_getter, user_tweets_setter, user_getter, friends_getter, friends_setter,
                ranking_setter)

        return ranker

    def get_community_ranker(self, function_name="SocialSupport"):
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        friends_getter = self.dao_module.get_user_friend_getter()
        ranking_setter = self.dao_module.get_ranking_setter()

        if function_name == "Consumption":
            ranker = CommunityConsumptionUtilityRanker(user_tweets_getter, friends_getter, ranking_setter)
        elif function_name == "Production":
            ranker = CommunityProductionUtilityRanker(user_tweets_getter, friends_getter, ranking_setter)
        else:
            ranker = CommunitySocialSupportRanker(user_tweets_getter, friends_getter, ranking_setter)
        return ranker

    def get_followers_ranker(self):
        pass

    def get_retweets_ranker(self):
        pass

    # Processing
    def get_tweet_processor(self):
        user_tweets_getter = self.dao_module.get_user_tweets_getter()
        user_processed_tweet_setter = self.dao_module.get_user_processed_tweets_setter()
        user_processed_tweet_getter = self.dao_module.get_user_processed_tweets_getter()

        tweet_processor = TweetProcessor(user_tweets_getter, user_processed_tweet_getter, user_processed_tweet_setter)

        return tweet_processor

    # Social Graph
    def get_social_graph_constructor(self, user_activity: str):
        local_neighbourhood_getter = self.dao_module.get_local_neighbourhood_getter(user_activity=user_activity)
        social_graph_setter = self.dao_module.get_social_graph_setter()

        social_graph_constructor = SocialGraphConstructor(
            local_neighbourhood_getter, social_graph_setter)

        return social_graph_constructor

    # User Word Frequency

    def get_user_word_frequency_processor(self):
        processed_tweet_getter = self.dao_module.get_processed_tweet_getter()
        user_word_frequency_getter = self.dao_module.get_user_word_frequency_getter()
        user_word_frequency_setter = self.dao_module.get_user_word_frequency_setter()
        global_word_frequency_getter = self.dao_module.get_global_word_frequency_getter()
        user_relative_word_frequency_setter = self.dao_module.get_user_relative_word_frequency_setter()

        user_word_frequency_processor = UserWordFrequencyProcessor(processed_tweet_getter, user_word_frequency_getter,
                                                                   user_word_frequency_setter,
                                                                   global_word_frequency_getter,
                                                                   user_relative_word_frequency_setter)

        return user_word_frequency_processor

    def get_cluster_word_frequency_processor(self):
        user_word_frequency_getter = self.dao_module.get_user_word_frequency_getter()
        cluster_word_frequency_getter = self.dao_module.get_cluster_word_frequency_getter()
        cluster_word_frequency_setter = self.dao_module.get_cluster_word_frequency_setter()
        cluster_relative_word_frequency_setter = self.dao_module.get_cluster_relative_word_frequency_setter()
        global_word_frequency_getter = self.dao_module.get_global_word_frequency_getter()
        user_word_frequency_processor = self.get_user_word_frequency_processor()

        cluster_word_frequency_processor = ClusterWordFrequencyProcessor(user_word_frequency_getter,
                                                                         cluster_word_frequency_getter,
                                                                         cluster_word_frequency_setter,
                                                                         global_word_frequency_getter,
                                                                         cluster_relative_word_frequency_setter,
                                                                         user_word_frequency_processor)

        return cluster_word_frequency_processor
