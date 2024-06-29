# SNACES

SNACES (Social Network Algorithm Contained Experiment System)
is a Python library for downloading and analyze Twitter data, by making
use of the Tweepy library and the Twitter API.

## Setup

### BlueSky Account

In order to make use of the BlueSky API, and the Atproto package, you will need
credential for the twitter API.

To retrieve these credentials sign up for a regular bluesky account

Create a file with this path `./conf/credentials.py` and enter your username and password in the file in this format:
```python
USER_NAME = "<Your Username>"
PASSWORD = "<Your Password>"
```

### Installing
Python 3.9 is required for the following installation steps.

Follow the instructions in the main README.md file to setup the environment.

## Running

1. The main program for core detection can be started by running 
`python detect_core_jaccard.py -n {seed_user} -act {user_activity}`. For example 
`python detect_core_jaccard.py -n "doctorvive.bsky.social" -act "user retweets"` for seed user "doctorvive.bsky.social" and user activity "user retweets".

2. The main program for community expansion can be started by running `python ./SNACES.py`. This will trigger the main program to loop, which will then prompt you to input options for which process to trigger.
Choose option 6 for community expansion.
