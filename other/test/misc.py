import datetime
import daemon

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
test_db = client['test']
nested_col = test_db['nestedCol']

nested_col.insert_one({
    'user': "Bob",
    'nest': [{'cond1': True, 'x': 5}, {'cond1': False, 'x': 5}]
})

pipeline = (
    [{
      '$project': {
         'user': True,
         'nest': {
            '$filter': {
               'input': "$nest",
               'as': "n",
               'cond': {'$ne': ['$$n.cond1', True]}}
            }
         }
      }
])
doc_list = nested_col.aggregate(pipeline)

for doc in doc_list:
    print(doc)


# db = client['Fatema']
# col = db['hardmaru']

# output_db = client['TwitterDownload']
# output_col = output_db['UserTweets']

# # generate user to tweets 
# user_to_tweets = {}
# for doc in col.find():
#     user = doc['user']['screen_name']
#     tweet_text = doc['full_text']

#     if user not in user_to_tweets:
#         user_to_tweets[user] = []

#     user_to_tweets[user].append({'text': tweet_text})

# # insert to output_col
# for user in user_to_tweets:
#     output_col.insert_one({
#         'user': user,
#         'tweets': user_to_tweets[user]
#     })














# def daterange(start_date, end_date):
#     for n in range(int ((end_date - start_date).days)):
#         yield start_date + datetime.timedelta(n)   

# # Convert Twitter Download old format to new format
# with daemon.DaemonContext(chroot_directory=None, working_directory='./'):
#     old_processed_db = client['RawTweetsDS']
#     new_processed_db = client['TwitterDownload']
#     new_processed_col = new_processed_db['GlobalTweets']

#     start_date = datetime.datetime(2020, 1, 23, 0, 0, 0)
#     end_date = datetime.datetime(2020, 7, 4, 0, 0, 0)

#     for date in daterange(start_date, end_date):
#         date = date.strftime("%Y-%m-%d")
#         processed_tweet_collection_name = "({})-RawTweets".format(date) 
#         old_procesed_col = old_processed_db[processed_tweet_collection_name]

#         for processed_doc in old_procesed_col.find():
#             tweet_words = processed_doc['text']
#             new_processed_col.insert_one({
#                 'text': tweet_words
#             })
