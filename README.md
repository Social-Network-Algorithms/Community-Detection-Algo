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
### MongoDB

You will need MongoDB for data storage. 

### Installing
Python 3.9 is required for the following installation steps.
1. Clone Git repository to your workspace
2. Run the install script `./scripts/install.sh`
3. Run `python ./setup.py` to setup the Pipfile
4. Run `pipenv shell` to start a pip environment using the pip file
  
Note that you might need to do the following in the pip environment:  
1. pip install python-dateutil
2. pip install matplotlib
3. create /core/log folder

### Configuration

The default path we are using is:
`/src/scripts/config/create_social_graph_and_cluster_config.yaml`

### Installing

See `requirements.txt` for the required packages. **Note:** The pygraphviz package may require additional installation steps. See [here](https://stackoverflow.com/questions/15661384/python-does-not-see-pygraphviz/71661788#71661788).

There may be some problems with the pipenv shell above. An alternative is to use a conda environment with Python 3.9. After installing conda and activating your environment, run `pip install -r clustering_trial_requirements.txt` to install the required packages.

If there are some issues with pip conflicting, while in the conda environment, try the following to create a virtual environment and install the required packages: 
```
python -m venv env
source env/bin/activate
pip install -r clustering_trial_requirements.txt
```

## Running
The main program for community detection consists of:
- Detection of influential users
- Expansion of the community
- Running tests to assess the quality of the community

and can be started by running
` python run_community_detection.py -n {seed_user}`.

For example
` python run_community_detection.py -n "doctorvive.bsky.social""` for seed user "doctorvive.bsky.social".

The results for the community users and the tests can be found under the data/{seed_user}/expansion and data/{seed_user}/tests directories respectively.

## Current Work

### dao module

The dao module includes all the getter and setters that connects the data storage with our program.

### model module

The model module includes the instances such as User and Tweets that are used in our program

### Utility Functions
The implementation of the user and community utility functions, including social support utility that is being used 
in our algorithm, can be found under `/src/process/community_ranking` and `/src/process/ranking`.

### Core Detection

The main code for core detection is in 
`/src/process/core_detection/`

### Community Expansion

The main code for community expansion is in 
`/src/process/community_expansion/`

### Quality tests
Some tests for assessing the quality of the final communities have been added 
in `/quality_tests/`
