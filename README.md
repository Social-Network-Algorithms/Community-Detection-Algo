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
The main program for community detection consisting of:
- Detection of influential users
- Expansion of the community
- Running tests to assess the quality of the community

can be started by running
` python run_community_detection.py -n {seed_user}`. For example
` python run_community_detection.py -n "doctorvive.bsky.social""` for seed user "doctorvive.bsky.social".

The results for the community users and the tests can be found under the data/{seed_user}/expansion and data/{seed_user}/tests directories respectively.

## Current Work

### dao module

The dao module includes all the getter and setters that connects the data storage with our program.

### model module

The model module includes the instances such as User and Tweets that are used in our program

### Utility Functions
The implementation of the user and community utility function, including social support utility that is being used 
in our algorithm can be found under `/src/process/community_ranking` and `/src/process/ranking`.

### Community Expansion

The main code for community expansion is in 
`/src/process/community_expansion/`

### Core Detection

The main code for community expansion is in 
`/src/process/core_detection/`