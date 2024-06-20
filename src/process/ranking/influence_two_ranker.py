from src.dao.user_tweets.getter.user_tweets_getter import UserTweetsGetter
from src.dao.user_tweets.setter.user_tweets_setter import UserTweetsSetter
from src.process.ranking.ranker import Ranker
from typing import Dict, List
from tqdm import tqdm

class InfluenceTwoRanker(Ranker):
	def __init__(self, twitter_getter, user_tweets_getter: UserTweetsGetter, user_tweets_setter: UserTweetsSetter,
				 friends_getter, friends_setter, ranking_setter):
		self.twitter_getter = twitter_getter
		self.user_tweets_getter = user_tweets_getter
		self.user_tweets_setter = user_tweets_setter
		self.friends_getter = friends_getter
		self.friends_setter = friends_setter
		self.ranking_setter = ranking_setter
		self.ranking_function_name = "influence two"

	def create_friends_dict(self, user_ids):
		friends = {}
		for user_id in user_ids:
			friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)
			if friends_of_user_id is None:
				_, friends_result = self.twitter_getter.get_friends_ids_by_user_id(user_id, None)
				self.friends_setter.store_friends(user_id, friends_result)
				friends_of_user_id = self.friends_getter.get_user_friends_ids(user_id)

			friends[user_id] = friends_of_user_id
		return friends

	def score_users(self, user_ids: List[str]):
		# Score users by summing up the percentage of tweets they make up in all followers' retweets
		scores = {user_id: [0,0] for user_id in user_ids} # Initialize all scores to 0

		tweets = []
		for id in user_ids:
			user_tweets = self.user_tweets_getter.get_user_tweets(id)
			if user_tweets is None:
				self.user_tweets_setter.store_tweets(id, self.twitter_getter.get_tweets_by_user_id(id, 600))
				user_tweets = self.user_tweets_getter.get_user_tweets(id)

			tweets += user_tweets
		valid_tweets = [tweet for tweet in tweets if tweet.retweet_user_id != tweet.user_id]

		# Define helper functions
		tweets_by_retweet_group = self._group_by_retweet_id(valid_tweets)
		def get_retweets_of_tweet_id(tweet_id):
			return tweets_by_retweet_group.get(str(tweet_id), [])
		def get_later_retweets_of_tweet_id(tweet_id, created_at):
			return [tweet for tweet in get_retweets_of_tweet_id(tweet_id) if tweet.created_at > created_at]

		retweets_by_retweeter = self._group_by_retweeter(valid_tweets)
		def get_num_retweets_by(id):
			return len(retweets_by_retweeter.get(id, []))

		friends = self.create_friends_dict(user_ids)
		def is_direct_follower(a, b): # 'b' is a follower of 'a'
			return a in friends.get(b, [])

		for id in tqdm(user_ids):
			user_tweets = [tweet for tweet in valid_tweets if str(tweet.user_id) == id]
			user_original_tweets = [tweet for tweet in user_tweets if tweet.retweet_id is None]
			user_retweets = [tweet for tweet in user_tweets if tweet.retweet_id is not None]
			followers_id = [other_id for other_id in user_ids if id != other_id and is_direct_follower(id, other_id)]
			retweets_of_original_tweets = []
			retweets_of_retweets = []

			for original_tweet in user_original_tweets:
				retweets = get_retweets_of_tweet_id(original_tweet.id)
				retweets_of_original_tweets.append(retweets)

			for user_retweet in user_retweets:
				retweets = get_later_retweets_of_tweet_id(user_retweet.retweet_id, user_retweet.created_at)
				retweets_of_retweets.append(retweets)

			for follower_id in followers_id:
				follower_score = 0
				# Score original tweets
				for i in range(len(retweets_of_original_tweets)):
					follower_score += 1 if any(str(rtw.user_id) == follower_id for rtw in retweets_of_original_tweets[i]) else 0
				# Score retweets
				for i in range(len(retweets_of_retweets)):
					follower_score += 1 if any(str(rtw.user_id) == follower_id for rtw in retweets_of_retweets[i]) else 0

				if get_num_retweets_by(follower_id) > 0:
					follower_score /= get_num_retweets_by(follower_id)
				scores[id][0] += follower_score
			scores[id][1] = len(user_tweets)

		return scores

	def _group_by_retweet_id(self, tweets) -> Dict:
		# Puts all tweets with the same retweet_id in the same list
		# Returns: A dictionary where the key is the retweet_id and
		# the value is the list of tweets with that retweet_id
		dict = {}
		for tweet in tweets:
			key = str(tweet.retweet_id)
			if key in dict:
				dict[key].append(tweet)
			else:
				dict[key] = [tweet]

		return dict

	def _group_by_retweeter(self, tweets) -> Dict:
		# Puts all tweets with the same retweeter in the same list
		# Returns: A dictionary where the key is the user_id of the retweeter and
		# the value is the list of tweets retweeted by the retweeter
		dict = {}
		for tweet in tweets:
			if tweet.retweet_id is None: # tweet is not a retweet
				continue
			key = str(tweet.user_id)
			if key in dict:
				dict[key].append(tweet)
			else:
				dict[key] = [tweet]

		return dict

